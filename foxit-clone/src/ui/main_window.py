import os
import shutil
import sys
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
from src.security.signatures import create_self_signed_cert, sign_pdf, validate_pdf
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

        self.ribbon = RibbonBar()
        self.setMenuWidget(self.ribbon)

        self.home_category = self.ribbon.addCategory("Home")
        file_panel = self.home_category.addPanel("File")
        open_btn = file_panel.addLargeButton("Open")
        open_btn.clicked.connect(self.open_file)

        tools_panel = self.home_category.addPanel("Tools")
        hand_btn = tools_panel.addLargeButton("Hand")
        hand_btn.clicked.connect(lambda: self._show_info("Use middle mouse button to pan."))
        select_btn = tools_panel.addLargeButton("Select")
        select_btn.clicked.connect(lambda: self._show_info("Click the page to pick text for editing or highlighting."))
        zoom_btn = tools_panel.addLargeButton("Zoom")
        zoom_btn.clicked.connect(lambda: self.on_zoom_requested(self.pdf_view.zoom_factor * 1.2))

        view_panel = self.home_category.addPanel("View")
        fit_width_btn = view_panel.addMediumButton("Fit Width")
        fit_width_btn.clicked.connect(lambda: self.on_zoom_requested(1.5))
        fit_page_btn = view_panel.addMediumButton("Fit Page")
        fit_page_btn.clicked.connect(lambda: self.on_zoom_requested(1.0))
        actual_size_btn = view_panel.addMediumButton("Actual Size")
        actual_size_btn.clicked.connect(lambda: self.on_zoom_requested(1.0))

        self.edit_category = self.ribbon.addCategory("Edit")
        edit_tools_panel = self.edit_category.addPanel("Edit Tools")
        edit_text_btn = edit_tools_panel.addLargeButton("Edit Text")
        edit_text_btn.clicked.connect(self.action_edit_text)
        edit_object_btn = edit_tools_panel.addLargeButton("Edit Object")
        edit_object_btn.clicked.connect(self.action_highlight_selection)

        insert_panel = self.edit_category.addPanel("Insert")
        image_btn = insert_panel.addMediumButton("Image")
        image_btn.clicked.connect(self.action_insert_image)
        link_btn = insert_panel.addMediumButton("Link")
        link_btn.clicked.connect(self.action_insert_link)
        text_box_btn = insert_panel.addMediumButton("Text Box")
        text_box_btn.clicked.connect(self.action_insert_text_box)

        self.organize_category = self.ribbon.addCategory("Organize")
        pages_panel = self.organize_category.addPanel("Pages")

        insert_page_btn = pages_panel.addLargeButton("Insert")
        insert_page_btn.clicked.connect(self.action_insert_page)

        delete_page_btn = pages_panel.addLargeButton("Delete")
        delete_page_btn.clicked.connect(self.action_delete_page)

        rotate_page_btn = pages_panel.addLargeButton("Rotate")
        rotate_page_btn.clicked.connect(self.action_rotate_page)

        transform_panel = self.organize_category.addPanel("Transform")
        split_btn = transform_panel.addMediumButton("Split")
        split_btn.clicked.connect(self.action_split_document)
        merge_btn = transform_panel.addMediumButton("Merge")
        merge_btn.clicked.connect(self.action_merge_document)

        self.protect_category = self.ribbon.addCategory("Protect")
        redaction_panel = self.protect_category.addPanel("Redaction")
        mark_redaction_btn = redaction_panel.addLargeButton("Mark for Redaction")
        mark_redaction_btn.clicked.connect(self.action_mark_redaction)
        apply_redaction_btn = redaction_panel.addLargeButton("Apply Redactions")
        apply_redaction_btn.clicked.connect(self.action_apply_redaction)

        sign_panel = self.protect_category.addPanel("Signatures")
        sign_document_btn = sign_panel.addLargeButton("Sign Document")
        sign_document_btn.clicked.connect(self.action_sign_document)
        validate_btn = sign_panel.addMediumButton("Validate")
        validate_btn.clicked.connect(self.action_validate_signature)

        self.view_category = self.ribbon.addCategory("View")
        nav_panel = self.view_category.addPanel("Navigation")
        bookmarks_btn = nav_panel.addLargeButton("Bookmarks")
        bookmarks_btn.clicked.connect(self.sidebar.show_bookmarks)
        thumbnails_btn = nav_panel.addLargeButton("Thumbnails")
        thumbnails_btn.clicked.connect(self.sidebar.show_thumbnails)
        ocr_btn = nav_panel.addLargeButton("OCR")
        ocr_btn.clicked.connect(self.action_run_ocr)

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

        self.current_page = 0
        self.total_pages = 0

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
        return True

    @Slot()
    def open_file(self):
        self.filepath, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if self.filepath:
            self.engine.load_document(self.filepath)
            self.current_page = 0
            self.total_pages = self.engine.get_page_count()
            self.selected_rect = None
            self.last_clicked_pdf_point = None
            self._reload_sidebar()
            self.renderer.request_render(self.current_page, zoom=1.5)
            self.ai_assistant.add_system_message(f"Opened {Path(self.filepath).name} with {self.total_pages} page(s).")

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
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Current Page As", f"page-{self.current_page + 1}.pdf", "PDF Files (*.pdf)")
        if not output_path:
            return
        out_doc = fitz.open()
        out_doc.insert_pdf(self.engine.doc, from_page=self.current_page, to_page=self.current_page)
        out_doc.save(output_path)
        out_doc.close()
        self.ai_assistant.add_system_message(f"Exported page {self.current_page + 1} to {Path(output_path).name}.")

    @Slot()
    def action_edit_text(self):
        page = self._current_page_obj()
        if page is None:
            return
        editor = TextEditor(page)
        span = None
        if self.last_clicked_pdf_point is not None:
            span = editor.find_span_at_point(self.last_clicked_pdf_point)
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
        rect = self.selected_rect
        if rect is None and self.last_clicked_pdf_point is not None:
            editor = TextEditor(page)
            span = editor.find_span_at_point(self.last_clicked_pdf_point)
            if span:
                rect = span["bbox"]
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
        image_path, _ = QFileDialog.getOpenFileName(self, "Insert image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
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
        rect = self.selected_rect
        if rect is None and self.last_clicked_pdf_point is not None:
            editor = TextEditor(page)
            span = editor.find_span_at_point(self.last_clicked_pdf_point)
            if span:
                rect = span["bbox"]
        if rect is None:
            QMessageBox.information(self, "Redaction", "Click text on the page first.")
            return
        page.add_redact_annot(fitz.Rect(rect), fill=(0, 0, 0))
        self._save_document()

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
            output_path, _ = QFileDialog.getSaveFileName(self, "Save OCR PDF", f"ocr-page-{self.current_page + 1}.pdf", "PDF Files (*.pdf)")
            if output_path:
                shutil.copyfile(pdf_path, output_path)
                self.ai_assistant.add_system_message(f"OCR output saved to {Path(output_path).name}.")

    @Slot()
    def action_sign_document(self):
        if not self._require_document():
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "Save signed PDF", "signed-output.pdf", "PDF Files (*.pdf)")
        if not output_path:
            return
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_path = os.path.join(temp_dir, "cert.pem")
            key_path = os.path.join(temp_dir, "key.pem")
            create_self_signed_cert(cert_path, key_path)
            sign_pdf(self.filepath, output_path, cert_path, key_path)
        self.ai_assistant.add_system_message(f"Signed document written to {Path(output_path).name}.")

    @Slot()
    def action_validate_signature(self):
        if not self._require_document():
            return
        message = validate_pdf(self.filepath)
        QMessageBox.information(self, "Signature validation", message)

    @Slot(float, float)
    def on_pdf_clicked(self, x, y):
        page = self._current_page_obj()
        if page is None:
            return
        pdf_point = self.pdf_view.map_ui_to_pdf(x, y, fitz.Matrix(self.pdf_view.zoom_factor, self.pdf_view.zoom_factor))
        self.last_clicked_pdf_point = (pdf_point.x, pdf_point.y)
        editor = TextEditor(page)
        span = editor.find_span_at_point(self.last_clicked_pdf_point)
        self.selected_rect = span["bbox"] if span else None
        if span:
            self.ai_assistant.add_system_message(f"Selected text: {span['text']}")

    @Slot(int)
    def on_page_requested(self, page_num):
        if 0 <= page_num < self.total_pages:
            self.current_page = page_num
            self.selected_rect = None
            self.last_clicked_pdf_point = None
            self._render_current_page()

    @Slot(float)
    def on_zoom_requested(self, zoom_factor):
        if self.filepath:
            bounded_zoom = max(0.25, min(zoom_factor, 5.0))
            self.renderer.request_render(self.current_page, zoom=bounded_zoom)

    @Slot(int, float, object)
    def on_render_completed(self, page_num, zoom, pixmap):
        if page_num == self.current_page:
            self.pdf_view.set_pixmap(pixmap, zoom)

    def closeEvent(self, event):
        self.renderer.stop()
        self.engine.close()
        super().closeEvent(event)
