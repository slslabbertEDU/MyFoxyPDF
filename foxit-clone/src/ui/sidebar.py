from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QListWidget, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Signal, Qt

class Sidebar(QWidget):
    page_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Thumbnails Tab
        self.thumbnails_list = QListWidget()
        self.thumbnails_list.itemClicked.connect(self._on_thumbnail_clicked)
        self.tabs.addTab(self.thumbnails_list, "Thumbnails")

        # Bookmarks Tab
        self.bookmarks_tree = QTreeWidget()
        self.bookmarks_tree.setHeaderHidden(True)
        self.tabs.addTab(self.bookmarks_tree, "Bookmarks")

    def _on_thumbnail_clicked(self, item):
        page_num = item.data(Qt.ItemDataRole.UserRole)
        if page_num is not None:
            self.page_requested.emit(page_num)

    def populate_thumbnails(self, page_count):
        self.thumbnails_list.clear()
        for i in range(page_count):
            item = self.thumbnails_list.addItem(f"Page {i + 1}")
            actual_item = self.thumbnails_list.item(i)
            actual_item.setData(Qt.ItemDataRole.UserRole, i)
