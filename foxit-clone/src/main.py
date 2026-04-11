import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from ui.sidebar import Sidebar
from ai.assistant import AIAssistant
from render.engine import RenderEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyFoxyPDF")
        self.resize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar, 1)

        # Viewer Area
        self.viewer_layout = QVBoxLayout()
        self.viewer_label = QLabel("PDF Viewer Area")
        self.viewer_label.setStyleSheet("background-color: #f0f0f0;")
        self.viewer_layout.addWidget(self.viewer_label)
        main_layout.addLayout(self.viewer_layout, 3)

        # AI Assistant
        self.ai_assistant = AIAssistant()
        main_layout.addWidget(self.ai_assistant, 1)

        self.engine = RenderEngine()

    def load_document(self, filepath: str):
        self.engine.load_document(filepath)
        count = self.engine.get_page_count()
        self.sidebar.populate_thumbnails(count)
        if count > 0:
            pixmap = self.engine.render_page(0)
            if not pixmap.isNull():
                self.viewer_label.setPixmap(pixmap)

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
