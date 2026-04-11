import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QFileDialog, QToolBar, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from ui.sidebar import Sidebar
from ai.assistant import AIAssistant
from render.engine import RenderEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyFoxyPDF")
        self.resize(1200, 800)

        self.engine = RenderEngine()
        self.current_page = 0
        self.zoom = 1.0

        self.setup_ui()

    def setup_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Splitter to hold Sidebar, PDF View, AI Assistant
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 1. Sidebar
        self.sidebar = Sidebar()
        splitter.addWidget(self.sidebar)

        # 2. PDF View area
        pdf_widget = QWidget()
        pdf_layout = QVBoxLayout(pdf_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.pdf_label = QLabel("No PDF loaded")
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.pdf_label)

        pdf_layout.addWidget(self.scroll_area)
        splitter.addWidget(pdf_widget)

        # 3. AI Assistant
        self.ai_assistant = AIAssistant()
        splitter.addWidget(self.ai_assistant)

        # Set initial splitter sizes
        splitter.setSizes([200, 700, 300])

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_pdf)
        toolbar.addAction(open_action)

        prev_action = QAction("Prev", self)
        prev_action.triggered.connect(self.prev_page)
        toolbar.addAction(prev_action)

        next_action = QAction("Next", self)
        next_action.triggered.connect(self.next_page)
        toolbar.addAction(next_action)

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.engine.load_document(file_path)
            self.current_page = 0
            self.zoom = 1.0

            # Populate sidebar
            pages_count = self.engine.get_page_count()
            self.sidebar.populate_thumbnails(pages_count)

            self.render_current_page()

    def render_current_page(self):
        pixmap = self.engine.render_page(self.current_page, self.zoom)
        if not pixmap.isNull():
            self.pdf_label.setPixmap(pixmap)
        else:
            self.pdf_label.setText("Failed to render page")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_current_page()

    def next_page(self):
        if self.current_page < self.engine.get_page_count() - 1:
            self.current_page += 1
            self.render_current_page()

    def zoom_in(self):
        self.zoom += 0.2
        self.render_current_page()

    def zoom_out(self):
        if self.zoom > 0.4:
            self.zoom -= 0.2
            self.render_current_page()

    def closeEvent(self, event):
        self.engine.close()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
