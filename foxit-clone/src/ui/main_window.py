import sys
import os

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog, QSplitter, QLabel, QHBoxLayout, QToolButton, QInputDialog, QMessageBox
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QIcon, QAction
from pyqtribbon import RibbonBar

from src.ui.pdf_view import PDFView
from src.render.engine import RenderEngine
from src.render.async_renderer import AsyncRenderer
from src.ui.sidebar import Sidebar
from src.ai.assistant import AIAssistant
from src.edit.page_manager import PageManager

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

        # 1. Home Tab
        self.home_category = self.ribbon.addCategory("Home")
        file_panel = self.home_category.addPanel("File")
        open_btn = file_panel.addLargeButton("Open")
        open_btn.clicked.connect(self.open_file)

        tools_panel = self.home_category.addPanel("Tools")
        tools_panel.addLargeButton("Hand")
        tools_panel.addLargeButton("Select")
        tools_panel.addLargeButton("Zoom")

        view_panel = self.home_category.addPanel("View")
        view_panel.addMediumButton("Fit Width")
        view_panel.addMediumButton("Fit Page")
        view_panel.addMediumButton("Actual Size")

        # 2. Edit Tab
        self.edit_category = self.ribbon.addCategory("Edit")
        edit_tools_panel = self.edit_category.addPanel("Edit Tools")
        edit_tools_panel.addLargeButton("Edit Text")
        edit_tools_panel.addLargeButton("Edit Object")

        insert_panel = self.edit_category.addPanel("Insert")
        insert_panel.addMediumButton("Image")
        insert_panel.addMediumButton("Link")
        insert_panel.addMediumButton("Text Box")

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
        transform_panel.addMediumButton("Split")
        transform_panel.addMediumButton("Merge")

        # 4. Protect Tab
        self.protect_category = self.ribbon.addCategory("Protect")
        redaction_panel = self.protect_category.addPanel("Redaction")
        redaction_panel.addLargeButton("Mark for Redaction")
        redaction_panel.addLargeButton("Apply Redactions")

        sign_panel = self.protect_category.addPanel("Signatures")
        sign_panel.addLargeButton("Sign Document")
        sign_panel.addMediumButton("Validate")

        # 5. View Tab
        self.view_category = self.ribbon.addCategory("View")
        nav_panel = self.view_category.addPanel("Navigation")
        nav_panel.addLargeButton("Bookmarks")
        nav_panel.addLargeButton("Thumbnails")

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
    def open_file(self):
        self.filepath, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if self.filepath:
            self.engine.load_document(self.filepath)
            self.current_page = 0
            self.total_pages = self.engine.get_page_count()
            self.sidebar.populate_thumbnails(self.filepath)
            self.renderer.request_render(self.current_page, zoom=2.0)

    def _save_and_reload(self):
        if not self.filepath or not self.engine.doc:
            return

        # Incremental save per requirements
        self.engine.doc.saveIncr()
        # Force refresh
        self.total_pages = self.engine.get_page_count()
        self.sidebar.populate_thumbnails(self.filepath)
        self.renderer.request_render(self.current_page, zoom=self.pdf_view.zoom_factor)

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

    def closeEvent(self, event):
        self.renderer.stop()
        self.engine.close()
        super().closeEvent(event)
