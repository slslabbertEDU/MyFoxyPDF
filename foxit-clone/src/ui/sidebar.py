from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Thumbnails tab
        self.thumbnails_tab = QWidget()
        thumbnails_layout = QVBoxLayout(self.thumbnails_tab)
        self.thumbnails_list = QListWidget()
        self.thumbnails_list.setViewMode(QListWidget.IconMode)
        self.thumbnails_list.setResizeMode(QListWidget.Adjust)
        self.thumbnails_list.setSpacing(10)
        thumbnails_layout.addWidget(self.thumbnails_list)
        self.tabs.addTab(self.thumbnails_tab, "Thumbnails")

        # Bookmarks tab
        self.bookmarks_tab = QWidget()
        bookmarks_layout = QVBoxLayout(self.bookmarks_tab)
        self.bookmarks_list = QListWidget()
        bookmarks_layout.addWidget(self.bookmarks_list)
        self.tabs.addTab(self.bookmarks_tab, "Bookmarks")

    def populate_thumbnails(self, count: int):
        self.thumbnails_list.clear()
        for i in range(count):
            item = QListWidgetItem(f"Page {i+1}")
            # we'd normally set an icon here with `item.setIcon()`
            item.setTextAlignment(Qt.AlignCenter)
            self.thumbnails_list.addItem(item)
