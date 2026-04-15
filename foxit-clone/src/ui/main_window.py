import os
import shutil
import tempfile
from pathlib import Path

import fitz
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from pyqtribbon import RibbonBar

from src.ai.assistant import AIAssistant
from src.edit.annotations import add_highlight
from src.edit.page_manager import PageManager
from src.edit.text_editor import TextEditor
from src.ocr.runner import OCRRunner
from src.render.async_renderer import AsyncRenderer
from src.render.engine import RenderEngine
from src.security.redaction import apply_redaction
from src.security.signatures import (
    create_self_signed_cert,
    export_validation_report,
    sign_pdf,
    validate_pdf,
)
from src.ui.pdf_view import PDFView
from src.ui.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyFoxyPDF Editor Pro")
        self.resize(1400, 900)

        self.filepath = None
        self.engine = RenderEngine()
        self.renderer = AsyncRenderer(self.engine)
        self.renderer.render_completed.connect(self.on_render_completed)

        self.selected_rect = None
        self.last_clicked_pdf_point = None
        self.status_message = "Ready"

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = Sidebar()
        self.sidebar.page_requested.connect(self.on_page_requested)
        self.sidebar.bookmark_requested.connect(self.on_page_requested)
        self.splitter.addWidget(self.sidebar)

        self.pdf_view = PDFView()
        self.pdf_view.zoom_requested.connect(self.on_zoom_requested)
        self.pdf_view.click_requested.connect(self.on_pdf_clicked)
        self.splitter.addWidget(self.pdf_view)

        self.ai_assistant = AIAssistant()
        self.splitter.addWidget(self.ai_assistant)

        self.splitter.setSizes([220, 900, 300])
        self.main_layout.addWidget(self.splitter)
        self.setCentralWidget(self.central_widget)

        self.ribbon = RibbonBar()
        self.setMenuWidget(self.ribbon)
        self._build_ribbon()

        self.current_page = 0
        self.total_pages = 0
        self.statusBar().showMessage(self.status_message)

    def _build_ribbon(self):
        self.home_category = self.ribbon.addCategory("Home")
        file_panel = self.home_category.addPanel("File")
        file_panel.addLargeButton("Open").clicked.connect(self.open_file)
        file_panel.addLargeButton("Save As").clicked.connect(self.action_save_as)

        tools_panel = self.home_category.addPanel("Tools")
        tools_panel.addLargeButton("Hand").clicked.connect(
            lambda: self._show_info("Use middle mouse button to pan.")
        )
        tools_panel.addLargeButton("Select").clicked.connect(
            lambda: self._show_info("Click the page to pick text for editing or highlighting.")
        )
        tools_panel.addLargeButton("Zoom").clicked.connect(
            lambda: self.on_zoom_requested(self.pdf_view.zoom_factor * 1.2)
        )

        view_panel = self.home_category.addPanel("View")
        view_panel.addMediumButton("Fit Width").clicked.connect(lambda: self.on_zoom_requested(1.5))
        view_panel.addMediumButton("Fit Page").clicked.connect(lambda: self.on_zoom_requested(1.0))
        view_panel.addMediumButton("Actual Size").clicked.connect(lambda: self.on_zoom_requested(1.0))

        self.edit_category = self.ribbon.addCategory("Edit")
        edit_tools_panel = self.edit_category.addPanel("Edit Tools")
        edit_tools_panel.addLargeButton("Edit Text").clicked.connect(self.action_edit_text)
        edit_tools_panel.addLargeButton("Edit Object").clicked.connect(self.action_highlight_selection)

        insert_panel = self.edit_category.addPanel("Insert")
        insert_panel.addMediumButton("Image").clicked.connect(self.action_insert_image)
        insert_panel.addMediumButton("Link").clicked.connect(self.action_insert_link)
        insert_panel.addMediumButton("Text Box").clicked.connect(self.action_insert_text_box)

        self.organize_category = self.ribbon.addCategory("Organize")
        pages_panel = self.organize_category.addPanel("Pages")
        pages_panel.addLargeButton("Insert").clicked.connect(self.action_insert_page)
        pages_panel.addLargeButton("Delete").clicked.connect(self.action_delete_page)
        pages_panel.addLargeButton("Rotate").clicked.connect(self.action_rotate_page)

        transform_panel = self.organize_category.addPanel("Transform")
        transform_panel.addMediumButton("Split").clicked.connect(self.action_split_document)
        transform_panel.addMediumButton("Merge").clicked.connect(self.action_merge_document)

        self.protect_category = self.ribbon.addCategory("Protect")
        redaction_panel = self.protect_category.addPanel("Redaction")
        redaction_panel.addLargeButton("Mark for Redaction").clicked.connect(self.action_mark_redaction)
        redaction_panel.addLargeButton("Apply Redactions").clicked.connect(self.action_apply_redaction)

        sign_panel = self.protect_category.addPanel("Signatures")
        sign_panel.addLargeButton("Sign Document").clicked.connect(self.action_sign_document)
        sign_panel.addMediumButton("Validate").clicked.connect(self.action_validate_signature)
        sign_panel.addMediumButton("Export Report").clicked.connect(self.action_export_validation_report)

        self.view_category = self.ribbon.addCategory("View")
        nav_panel = self.view_category.addPanel("Navigation")
        nav_panel.addLargeButton("Bookmarks").clicked.connect(self.sidebar.show_bookmarks)
        nav_panel.addLargeButton("Thumbnails").clicked.connect(self.sidebar.show_thumbnails)
        nav_panel.addLargeButton("OCR").clicked.connect(self.action_run_ocr)

    def _set_status(self, message):
        self.status_message = message
        self.statusBar().showMessage(message)
        self.ai_assistant.add_system_message(message)

    def _show_info(self, message):
        QMessageBox.information(self, "MyFoxyPDF", message)

    def _require_document(self):
        if not self.engine.doc or not self.filepath:
            QMessageBox.warning(self, "No document", "Open a PDF first.")
            return False
        return True

    def _current_page_obj(self):
        if not self._require_document():
            return None
        return self.engine.doc[self.current_page]

    def _reset_selection(self):
        self.selected_rect = None
        self.last_clicked_pdf_point = None

    def _render_current_page(self):
        if self.filepath:
            self.renderer.request_render(self.current_page, zoom=self.pdf_view.zoom_factor or 1.0)

    def _reload_sidebar(self):
        if self.filepath:
            self.sidebar.populate_from_document(self.engine.doc, self.filepath)

    def _save_document(self):
        if not self._require_document():
            return False
        self.engine.doc.saveIncr()
        self.total_pages = self.engine.get_page_count()
        self.current_page = min(self.current_page, max(0, self.total_pages - 1))
        self._reload_sidebar()
        self._render_current_page()
        self._set_status(f"Saved {Path(self.filepath).name}")
        return True

    def _replace_document(self, new_path):
        if self.engine.doc:
            self.engine.close()
        self.filepath = str(new_path)
        self.engine.load_document(self.filepath)
        self.total_pages = self.engine.get_page_count()
        self.current_page = min(self.current_page, max(0, self.total_pages - 1))
        self._reset_selection()
        self._reload_sidebar()
        self._render_current_page()

    @Slot()
    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if filepath:
            self.filepath = filepath
            self.engine.load_document(self.filepath)
            self.current_page = 0
            self.total_pages = self.engine.get_page_count()
            self._reset_selection()
            self._reload_sidebar()
            self.renderer.request_render(self.current_page, zoom=1.5)
            self._set_status(f"Opened {Path(self.filepath).name} with {self.total_pages} page(s).")

    @Slot()
    def action_save_as(self):
        if not self._require_document():
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", Path(self.filepath).name, "PDF Files (*.pdf)")
        if not output_path:
            return
        self.engine.doc.save(output_path)
        self._replace_document(output_path)
        self._set_status(f"Saved copy as {Path(output_path).name}")

    @Slot()
    def action_insert_page(self):
        if not self._require_document():
            return
        PageManager(self.engine.doc).insert_empty_page(self.current_page + 1)
        self.current_page = min(self.current_page + 1, self.engine.get_page_count() - 1)
        self._save_document()

    @Slot()
    def action_delete_page(self):
        if not self._require_document():
            return
        if self.total_pages <= 1:
            QMessageBox.warning(self, "Delete page", "Cannot delete the only page in the document.")
            return
        if PageManager(self.engine.doc).delete_page(self.current_page):
            self.current_page = max(0, self.current_page - 1)
            self._save_document()

    @Slot()
    def action_rotate_page(self):
        if not self._require_document():
            return
        PageManager(self.engine.doc).rotate_page(self.current_page, 90)
        self._save_document()

    @Slot()
    def action_merge_document(self):
        if not self._require_document():
            return
        other_pdf, _ = QFileDialog.getOpenFileName(self, "Merge PDF", "", "PDF Files (*.pdf)")
        if not other_pdf:
            return
        PageManager(self.engine.doc).merge_pdf(other_pdf, self.current_page + 1)
        self._save_document()

    @Slot()
    def action_split_document(self):
        if not self._require_document():
            return
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Current Page As",
            f"page-{self.current_page + 1}.pdf",
            "PDF Files (*.pdf)",
        )
        if not output_path:
            return
        out_doc = fitz.open()
        out_doc.insert_pdf(self.engine.doc, from_page=self.current_page, to_page=self.current_page)
        out_doc.save(output_path)
        out_doc.close()
        self._set_status(f"Exported page {self.current_page + 1} to {Path(output_path).name}.")

    @Slot()
    def action_edit_text(self):
        page = self._current_page_obj()
        if page is None:
            return
        editor = TextEditor(page)
        span = editor.find_span_at_point(self.last_clicked_pdf_point) if self.last_clicked_pdf_point else None
        if span is None:
            spans = editor.get_text_spans()
            span = spans[0] if spans else None
        if span is None:
            QMessageBox.information(self, "Edit text", "No editable text found on this page.")
            return
        new_text, ok = QInputDialog.getText(self, "Edit text", "Replacement text:", text=span["text"])
        if ok and new_text and new_text != span["text"]:
            editor.redact_and_replace_text(span["bbox"], span["origin"], new_text, fontsize=span["size"])
            self._save_document()

    @Slot()
    def action_highlight_selection(self):
        page = self._current_page_obj()
        if page is None:
            return
        rect = self._selected_or_span_rect(page)
        if rect is None:
            QMessageBox.information(self, "Highlight", "Click text on the page first.")
            return
        add_highlight(page, rect)
        self._save_document()

    @Slot()
    def action_insert_text_box(self):
        page = self._current_page_obj()
        if page is None:
            return
        text, ok = QInputDialog.getText(self, "Insert text box", "Text:")
        if not ok or not text:
            return
        point = self.last_clicked_pdf_point or (72, 72)
        page.insert_textbox(fitz.Rect(point[0], point[1], point[0] + 200, point[1] + 60), text, fontsize=12)
        self._save_document()

    @Slot()
    def action_insert_link(self):
        page = self._current_page_obj()
        if page is None:
            return
        url, ok = QInputDialog.getText(self, "Insert link", "URL:", text="https://")
        if not ok or not url:
            return
        if not (url.startswith("https://") or url.startswith("http://")):
            QMessageBox.warning(self, "Insert link", "Only http:// or https:// URLs are allowed.")
            return
        point = self.last_clicked_pdf_point or (72, 72)
        rect = fitz.Rect(point[0], point[1], point[0] + 180, point[1] + 30)
        page.insert_textbox(rect, url, fontsize=11)
        page.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": url})
        self._save_document()

    @Slot()
    def action_insert_image(self):
        page = self._current_page_obj()
        if page is None:
            return
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Insert image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not image_path:
            return
        point = self.last_clicked_pdf_point or (72, 72)
        rect = fitz.Rect(point[0], point[1], point[0] + 200, point[1] + 200)
        page.insert_image(rect, filename=image_path)
        self._save_document()

    @Slot()
    def action_mark_redaction(self):
        page = self._current_page_obj()
        if page is None:
            return
        rect = self._selected_or_span_rect(page)
        if rect is None:
            QMessageBox.information(self, "Redaction", "Click text on the page first.")
            return
        page.add_redact_annot(fitz.Rect(rect), fill=(0, 0, 0))
        self._set_status("Marked selection for redaction.")
        self._render_current_page()

    @Slot()
    def action_apply_redaction(self):
        page = self._current_page_obj()
        if page is None:
            return
        if self.selected_rect is not None:
            apply_redaction(page, self.selected_rect)
        else:
            page.apply_redactions()
        self._save_document()

    @Slot()
    def action_run_ocr(self):
        if not self._require_document():
            return
        runner = OCRRunner()
        if not runner.is_available():
            QMessageBox.warning(self, "OCR", "Tesseract is not installed or not in PATH.")
            return
        with tempfile.TemporaryDirectory() as temp_dir:
            pix = self.engine.doc[self.current_page].get_pixmap(matrix=fitz.Matrix(2, 2))
            image_path = os.path.join(temp_dir, "ocr_input.png")
            pix.save(image_path)
            output_base = os.path.join(temp_dir, "ocr_output")
            pdf_path = runner.run_ocr(image_path, output_base)
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save OCR PDF",
                f"ocr-page-{self.current_page + 1}.pdf",
                "PDF Files (*.pdf)",
            )
            if output_path:
                shutil.copyfile(pdf_path, output_path)
                self._set_status(f"OCR output saved to {Path(output_path).name}.")

    @Slot()
    def action_sign_document(self):
        if not self._require_document():
            return
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save signed PDF",
            "signed-output.pdf",
            "PDF Files (*.pdf)",
        )
        if not output_path:
            return
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_path = os.path.join(temp_dir, "cert.pem")
            key_path = os.path.join(temp_dir, "key.pem")
            create_self_signed_cert(cert_path, key_path)
            signed_path = sign_pdf(self.filepath, output_path, cert_path, key_path)
        self._set_status(f"Signed document written to {Path(signed_path).name}.")

    @Slot()
    def action_validate_signature(self):
        if not self._require_document():
            return
        result = validate_pdf(self.filepath)
        QMessageBox.information(self, "Signature validation", result["message"])
        self._set_status(result["message"])

    @Slot()
    def action_export_validation_report(self):
        if not self._require_document():
            return
        result = validate_pdf(self.filepath)
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export validation report",
            "validation-report.txt",
            "Text Files (*.txt)",
        )
        if not output_path:
            return
        report_path = export_validation_report(self.filepath, result, output_path)
        self._set_status(f"Validation report saved to {Path(report_path).name}.")

    def _selected_or_span_rect(self, page):
        if self.selected_rect is not None:
            return self.selected_rect
        if self.last_clicked_pdf_point is None:
            return None
        span = TextEditor(page).find_span_at_point(self.last_clicked_pdf_point)
        return span["bbox"] if span else None

    @Slot(float, float)
    def on_pdf_clicked(self, x, y):
        page = self._current_page_obj()
        if page is None:
            return
        pdf_point = self.pdf_view.map_ui_to_pdf(
            x,
            y,
            fitz.Matrix(self.pdf_view.zoom_factor, self.pdf_view.zoom_factor),
        )
        self.last_clicked_pdf_point = (pdf_point.x, pdf_point.y)
        span = TextEditor(page).find_span_at_point(self.last_clicked_pdf_point)
        self.selected_rect = span["bbox"] if span else None
        if span:
            self._set_status(f"Selected text: {span['text']}")

    @Slot(int)
    def on_page_requested(self, page_num):
        if 0 <= page_num < self.total_pages:
            self.current_page = page_num
            self._reset_selection()
            self._render_current_page()
            self.statusBar().showMessage(f"Page {self.current_page + 1} of {self.total_pages}")

    @Slot(float)
    def on_zoom_requested(self, zoom_factor):
        if self.filepath:
            bounded_zoom = max(0.25, min(zoom_factor, 5.0))
            self.renderer.request_render(self.current_page, zoom=bounded_zoom)
            self.statusBar().showMessage(f"Zoom {bounded_zoom:.2f}x")

    @Slot(int, float, object)
    def on_render_completed(self, page_num, zoom, pixmap):
        if page_num == self.current_page:
            self.pdf_view.set_pixmap(pixmap, zoom)

    def closeEvent(self, event):
        self.renderer.stop()
        self.engine.close()
        super().closeEvent(event)
