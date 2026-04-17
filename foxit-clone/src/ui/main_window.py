import sys
import os

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog, QSplitter, QLabel, QHBoxLayout, QToolButton, QInputDialog, QMessageBox, QGraphicsView
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QIcon, QAction
from pyqtribbon import RibbonBar
import fitz

from src.ui.pdf_view import PDFView
from src.render.engine import RenderEngine
from src.render.async_renderer import AsyncRenderer
from src.ui.sidebar import Sidebar
from src.ai.assistant import AIAssistant
from src.edit.page_manager import PageManager
from src.edit.text_editor import TextEditor
from src.security.redaction import apply_redaction
from src.security.signatures import create_self_signed_cert, sign_pdf

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyFoxyPDF Editor Pro")
        self.resize(1400, 900)

        self.filepath = None
        self.engine = RenderEngine()
        self.renderer = AsyncRenderer(self.engine)
        self.renderer.render_completed.connect(self.on_render_completed)

        self.ribbon = RibbonBar()
        self.setMenuWidget(self.ribbon)

        self.current_interaction_mode = "select"
        self.redaction_rects = []
        self.pending_image_path = None

        # 1. Home Tab
        self.home_category = self.ribbon.addCategory("Home")
        file_panel = self.home_category.addPanel("File")
        open_btn = file_panel.addLargeButton("Open")
        open_btn.clicked.connect(self.open_file)

        tools_panel = self.home_category.addPanel("Tools")
        btn_hand = tools_panel.addLargeButton("Hand")
        btn_hand.clicked.connect(self.action_hand_tool)
        btn_select = tools_panel.addLargeButton("Select")
        btn_select.clicked.connect(self.action_select_tool)
        btn_zoom = tools_panel.addLargeButton("Zoom")
        btn_zoom.clicked.connect(self.action_zoom_tool)

        view_panel = self.home_category.addPanel("View")
        btn_fit_width = view_panel.addMediumButton("Fit Width")
        btn_fit_width.clicked.connect(self.action_fit_width)
        btn_fit_page = view_panel.addMediumButton("Fit Page")
        btn_fit_page.clicked.connect(self.action_fit_page)
        btn_actual_size = view_panel.addMediumButton("Actual Size")
        btn_actual_size.clicked.connect(self.action_actual_size)

        # 2. Edit Tab
        self.edit_category = self.ribbon.addCategory("Edit")
        edit_tools_panel = self.edit_category.addPanel("Edit Tools")
        btn_edit_text = edit_tools_panel.addLargeButton("Edit Text")
        btn_edit_text.clicked.connect(self.action_edit_text)
        btn_edit_obj = edit_tools_panel.addLargeButton("Edit Object")
        btn_edit_obj.clicked.connect(self.action_edit_object)

        insert_panel = self.edit_category.addPanel("Insert")
        btn_image = insert_panel.addMediumButton("Image")
        btn_image.clicked.connect(self.action_insert_image)
        btn_link = insert_panel.addMediumButton("Link")
        btn_link.clicked.connect(self.action_insert_link)
        btn_text_box = insert_panel.addMediumButton("Text Box")
        btn_text_box.clicked.connect(self.action_insert_text_box)

        # 3. Organize Tab
        self.organize_category = self.ribbon.addCategory("Organize")
        pages_panel = self.organize_category.addPanel("Pages")

        insert_page_btn = pages_panel.addLargeButton("Insert")
        insert_page_btn.clicked.connect(self.action_insert_page)

        delete_page_btn = pages_panel.addLargeButton("Delete")
        delete_page_btn.clicked.connect(self.action_delete_page)

        rotate_page_btn = pages_panel.addLargeButton("Rotate")
        rotate_page_btn.clicked.connect(self.action_rotate_page)

        transform_panel = self.organize_category.addPanel("Transform")
        btn_split = transform_panel.addMediumButton("Split")
        btn_split.clicked.connect(self.action_split_document)
        btn_merge = transform_panel.addMediumButton("Merge")
        btn_merge.clicked.connect(self.action_merge_pdfs)

        # 4. Protect Tab
        self.protect_category = self.ribbon.addCategory("Protect")
        redaction_panel = self.protect_category.addPanel("Redaction")
        btn_mark_redact = redaction_panel.addLargeButton("Mark for Redaction")
        btn_mark_redact.clicked.connect(self.action_mark_redaction)
        btn_apply_redact = redaction_panel.addLargeButton("Apply Redactions")
        btn_apply_redact.clicked.connect(self.action_apply_redactions)

        sign_panel = self.protect_category.addPanel("Signatures")
        btn_sign = sign_panel.addLargeButton("Sign Document")
        btn_sign.clicked.connect(self.action_sign_document)
        btn_validate = sign_panel.addMediumButton("Validate")
        btn_validate.clicked.connect(self.action_validate_signature)

        # 5. View Tab
        self.view_category = self.ribbon.addCategory("View")
        nav_panel = self.view_category.addPanel("Navigation")
        btn_bookmarks = nav_panel.addLargeButton("Bookmarks")
        btn_bookmarks.clicked.connect(lambda: self.sidebar.tabs.setCurrentIndex(1))
        btn_thumbnails = nav_panel.addLargeButton("Thumbnails")
        btn_thumbnails.clicked.connect(lambda: self.sidebar.tabs.setCurrentIndex(0))

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 3-Way Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = Sidebar()
        self.sidebar.page_requested.connect(self.on_page_requested)
        self.splitter.addWidget(self.sidebar)

        self.pdf_view = PDFView()
        self.pdf_view.zoom_requested.connect(self.on_zoom_requested)
        self.pdf_view.click_requested.connect(self.on_pdf_clicked)
        self.pdf_view.rubberband_selected.connect(self.on_rubberband_selected)
        self.splitter.addWidget(self.pdf_view)

        # Right Panel: AI Assistant
        self.ai_assistant = AIAssistant()
        self.splitter.addWidget(self.ai_assistant)

        self.splitter.setSizes([200, 900, 300])

        self.main_layout.addWidget(self.splitter)
        self.setCentralWidget(self.central_widget)

        self.current_page = 0
        self.total_pages = 0

    @Slot()
    def not_implemented(self, feature_name):
        QMessageBox.information(self, "Feature Not Implemented", f"The '{feature_name}' feature is not yet implemented.")

    @Slot()
    def open_file(self):
        self.filepath, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if self.filepath:
            self.engine.load_document(self.filepath)
            self.current_page = 0
            self.total_pages = self.engine.get_page_count()
            self.sidebar.populate_thumbnails(self.filepath)
            self.renderer.request_render(self.current_page, zoom=1.0)

    def _save_and_reload(self):
        if not self.filepath or not self.engine.doc:
            return
        self.engine.doc.saveIncr()
        self.total_pages = self.engine.get_page_count()
        self.sidebar.populate_thumbnails(self.filepath)
        self.renderer.request_render(self.current_page, zoom=self.pdf_view.zoom_factor)

    @Slot()
    def action_hand_tool(self):
        self.pdf_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.current_interaction_mode = "hand"

    @Slot()
    def action_select_tool(self):
        self.pdf_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.current_interaction_mode = "select"

    @Slot()
    def action_zoom_tool(self):
        val, ok = QInputDialog.getDouble(self, "Zoom", "Enter zoom factor:", self.pdf_view.zoom_factor, 0.1, 10.0, 2)
        if ok:
            self.renderer.request_render(self.current_page, zoom=val)

    @Slot()
    def action_fit_width(self):
        if not self.engine.doc or not self.pdf_view.scene.items(): return
        item = self.pdf_view.current_item
        view_width = self.pdf_view.viewport().width()
        # Original width is item width / zoom_factor
        orig_width = item.boundingRect().width() / self.pdf_view.zoom_factor
        if orig_width > 0:
            zoom = view_width / orig_width
            self.renderer.request_render(self.current_page, zoom=zoom)

    @Slot()
    def action_fit_page(self):
        if not self.engine.doc or not self.pdf_view.scene.items(): return
        item = self.pdf_view.current_item
        view_height = self.pdf_view.viewport().height()
        view_width = self.pdf_view.viewport().width()

        orig_height = item.boundingRect().height() / self.pdf_view.zoom_factor
        orig_width = item.boundingRect().width() / self.pdf_view.zoom_factor

        if orig_height > 0 and orig_width > 0:
            zoom_h = view_height / orig_height
            zoom_w = view_width / orig_width
            zoom = min(zoom_h, zoom_w)
            self.renderer.request_render(self.current_page, zoom=zoom)

    @Slot()
    def action_actual_size(self):
        self.renderer.request_render(self.current_page, zoom=1.0)

    @Slot()
    def action_edit_text(self):
        self.pdf_view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.current_interaction_mode = "edit_text"
        QMessageBox.information(self, "Edit Text", "Click on any text in the document to edit it.")

    @Slot()
    def action_edit_object(self):
        # We don't have a complex object editor backend in edit/ yet, so we'll use a placeholder interaction mode
        self.current_interaction_mode = "edit_object"
        QMessageBox.information(self, "Edit Object", "Click on an object to attempt to select it. (Note: Only simple objects supported)")

    @Slot()
    def action_insert_image(self):
        if not self.engine.doc: return
        img_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if img_path:
            self.pending_image_path = img_path
            self.pdf_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.current_interaction_mode = "insert_image"
            QMessageBox.information(self, "Insert Image", "Draw a rectangle where you want the image to appear.")

    @Slot()
    def action_insert_link(self):
        if not self.engine.doc: return
        self.pdf_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.current_interaction_mode = "insert_link"
        QMessageBox.information(self, "Insert Link", "Draw a rectangle where the link should be placed.")

    @Slot()
    def action_insert_text_box(self):
        if not self.engine.doc: return
        self.pdf_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.current_interaction_mode = "insert_text_box"
        QMessageBox.information(self, "Insert Text Box", "Draw a rectangle for the text box.")

    @Slot()
    def action_insert_page(self):
        if not self.engine.doc: return
        manager = PageManager(self.engine.doc)
        manager.insert_empty_page(self.current_page + 1)
        self._save_and_reload()

    @Slot()
    def action_delete_page(self):
        if not self.engine.doc: return
        manager = PageManager(self.engine.doc)
        if manager.delete_page(self.current_page):
            self.current_page = max(0, self.current_page - 1)
            self._save_and_reload()

    @Slot()
    def action_rotate_page(self):
        if not self.engine.doc: return
        manager = PageManager(self.engine.doc)
        manager.rotate_page(self.current_page, 90)
        self._save_and_reload()

    @Slot()
    def action_split_document(self):
        if not self.engine.doc: return
        output_pdf, _ = QFileDialog.getSaveFileName(self, "Save Split PDF", "", "PDF Files (*.pdf)")
        if output_pdf:
            new_doc = fitz.open()
            new_doc.insert_pdf(self.engine.doc, from_page=self.current_page, to_page=self.current_page)
            new_doc.save(output_pdf)
            new_doc.close()
            QMessageBox.information(self, "Split Document", f"Saved current page to {output_pdf}")

    @Slot()
    def action_merge_pdfs(self):
        if not self.engine.doc: return
        other_pdf, _ = QFileDialog.getOpenFileName(self, "Select PDF to Merge", "", "PDF Files (*.pdf)")
        if other_pdf:
            manager = PageManager(self.engine.doc)
            manager.merge_pdf(other_pdf, at_index=self.current_page + 1)
            self._save_and_reload()

    @Slot()
    def action_mark_redaction(self):
        self.pdf_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.current_interaction_mode = "redact"
        QMessageBox.information(self, "Mark Redaction", "Draw a rectangle over the area you want to redact.")

    @Slot()
    def action_apply_redactions(self):
        if not self.engine.doc or not self.redaction_rects: return
        for page_num, rect in self.redaction_rects:
            page = self.engine.doc[page_num]
            apply_redaction(page, rect)
        self.redaction_rects.clear()
        self._save_and_reload()

    @Slot()
    def action_sign_document(self):
        if not self.filepath: return
        output_pdf, _ = QFileDialog.getSaveFileName(self, "Save Signed PDF", "", "PDF Files (*.pdf)")
        if output_pdf:
            cert_path = "temp_cert.pem"
            key_path = "temp_key.pem"
            try:
                create_self_signed_cert(cert_path, key_path)
                sign_pdf(self.filepath, output_pdf, cert_path, key_path)
                QMessageBox.information(self, "Success", f"Document signed and saved to {output_pdf}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to sign document: {str(e)}")
            finally:
                if os.path.exists(cert_path): os.remove(cert_path)
                if os.path.exists(key_path): os.remove(key_path)

    @Slot()
    def action_validate_signature(self):
        if not self.filepath: return
        # Basic validation placeholder logic as PyHanko validation requires cert trust setup
        try:
            from pyhanko.sign.validation import validate_pdf_signature
            from pyhanko.pdf_utils.reader import PdfFileReader
            with open(self.filepath, 'rb') as f:
                r = PdfFileReader(f)
                sig_fields = r.embedded_signatures
                if not sig_fields:
                    QMessageBox.information(self, "Validation", "No signatures found in document.")
                else:
                    QMessageBox.information(self, "Validation", f"Found {len(sig_fields)} signature(s). Full validation requires trust configuration.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not analyze signatures: {e}")

    @Slot(int)
    def on_page_requested(self, page_num):
        if 0 <= page_num < self.total_pages:
            self.current_page = page_num
            self.renderer.request_render(self.current_page, zoom=self.pdf_view.zoom_factor)

    @Slot(float)
    def on_zoom_requested(self, zoom_factor):
        if self.filepath:
            self.renderer.request_render(self.current_page, zoom=zoom_factor)

    @Slot(int, float, object)
    def on_render_completed(self, page_num, zoom, pixmap):
        if page_num == self.current_page:
            self.pdf_view.set_pixmap(pixmap, zoom)

    @Slot(float, float)
    def on_pdf_clicked(self, ui_x, ui_y):
        if not self.engine.doc: return

        page = self.engine.doc[self.current_page]
        mat = fitz.Matrix(self.pdf_view.zoom_factor, self.pdf_view.zoom_factor)
        pdf_point = self.pdf_view.map_ui_to_pdf(ui_x, ui_y, mat)

        if self.current_interaction_mode == "edit_text":
            editor = TextEditor(page)
            span = editor.find_span_at_point((pdf_point.x, pdf_point.y))
            if span:
                new_text, ok = QInputDialog.getText(self, "Edit Text", "New text:", text=span['text'])
                if ok and new_text != span['text']:
                    editor.redact_and_replace_text(span['bbox'], span['origin'], new_text, fontsize=span['size'])
                    self._save_and_reload()
        elif self.current_interaction_mode == "edit_object":
            QMessageBox.information(self, "Edit Object", f"Clicked object at PDF coordinates: {pdf_point.x:.2f}, {pdf_point.y:.2f}")

    @Slot(float, float, float, float)
    def on_rubberband_selected(self, x, y, w, h):
        if not self.engine.doc: return

        # Convert scene rectangle to PDF coordinates using the inverse matrix
        mat = fitz.Matrix(self.pdf_view.zoom_factor, self.pdf_view.zoom_factor)

        top_left = self.pdf_view.map_ui_to_pdf(x, y, mat)
        bottom_right = self.pdf_view.map_ui_to_pdf(x + w, y + h, mat)
        pdf_rect = fitz.Rect(top_left.x, top_left.y, bottom_right.x, bottom_right.y)

        page = self.engine.doc[self.current_page]

        if self.current_interaction_mode == "redact":
            self.redaction_rects.append((self.current_page, pdf_rect))
            QMessageBox.information(self, "Redaction Marked", "Redaction area marked. Click 'Apply Redactions' to finalize.")
        elif self.current_interaction_mode == "insert_image" and self.pending_image_path:
            page.insert_image(pdf_rect, filename=self.pending_image_path)
            self.pending_image_path = None
            self._save_and_reload()
        elif self.current_interaction_mode == "insert_link":
            url, ok = QInputDialog.getText(self, "Insert Link", "URL:")
            if ok and url:
                page.insert_link({"kind": fitz.LINK_URI, "from": pdf_rect, "uri": url})
                self._save_and_reload()
        elif self.current_interaction_mode == "insert_text_box":
            text, ok = QInputDialog.getText(self, "Insert Text Box", "Text:")
            if ok and text:
                page.insert_textbox(pdf_rect, text, fontsize=12, fontname="helv", color=(0,0,0))
                self._save_and_reload()

    def closeEvent(self, event):
        self.renderer.stop()
        self.engine.close()
        super().closeEvent(event)
