from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QListWidget, QListWidgetItem, QLabel

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Thumbnails Tab
        self.thumbnails_tab = QWidget()
        self.thumbnails_layout = QVBoxLayout(self.thumbnails_tab)
        self.thumbnails_layout.setContentsMargins(0, 0, 0, 0)
        self.thumbnails_list = QListWidget()
        self.thumbnails_layout.addWidget(self.thumbnails_list)
        self.tabs.addTab(self.thumbnails_tab, "Thumbnails")

        # Bookmarks Tab
        self.bookmarks_tab = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_tab)
        self.bookmarks_layout.setContentsMargins(0, 0, 0, 0)
        self.bookmarks_list = QListWidget()
        self.bookmarks_layout.addWidget(self.bookmarks_list)
        self.tabs.addTab(self.bookmarks_tab, "Bookmarks")

    def populate_thumbnails(self, count: int):
        self.thumbnails_list.clear()
        for i in range(count):
            item = QListWidgetItem(f"Page {i + 1}")
            self.thumbnails_list.addItem(item)
