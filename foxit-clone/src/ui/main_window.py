import sys
import os

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog, QSplitter, QLabel, QHBoxLayout, QToolButton
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QIcon, QAction
from pyqtribbon import RibbonBar

from .pdf_view import PDFView
from render.engine import RenderEngine
from render.async_renderer import AsyncRenderer
from .sidebar import Sidebar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyFoxyPDF Editor Pro")
        self.resize(1200, 800)

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
        pages_panel.addLargeButton("Insert")
        pages_panel.addLargeButton("Delete")
        pages_panel.addLargeButton("Rotate")

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

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = Sidebar()
        self.sidebar.page_requested.connect(self.on_page_requested)
        self.splitter.addWidget(self.sidebar)

        self.pdf_view = PDFView()
        self.splitter.addWidget(self.pdf_view)

        self.splitter.setSizes([200, 800])

        self.main_layout.addWidget(self.splitter)
        self.setCentralWidget(self.central_widget)

        self.current_page = 0
        self.total_pages = 0

    @Slot()
    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if filepath:
            self.engine.load_document(filepath)
            self.current_page = 0
            self.total_pages = self.engine.get_page_count()
            self.sidebar.populate_thumbnails(self.total_pages)
            self.renderer.request_render(self.current_page, zoom=2.0)

    @Slot(int)
    def on_page_requested(self, page_num):
        if 0 <= page_num < self.total_pages:
            self.current_page = page_num
            self.renderer.request_render(self.current_page, zoom=2.0)

    @Slot(int, object)
    def on_render_completed(self, page_num, pixmap):
        if page_num == self.current_page:
            self.pdf_view.set_pixmap(pixmap)

    def closeEvent(self, event):
        self.renderer.stop()
        self.engine.close()
        super().closeEvent(event)
