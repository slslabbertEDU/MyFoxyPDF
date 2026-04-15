from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
import fitz


class Sidebar(QWidget):
    page_requested = Signal(int)
    bookmark_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.thumbnails_list = QListWidget()
        self.thumbnails_list.setIconSize(QSize(100, 150))
        self.thumbnails_list.itemClicked.connect(self._on_thumbnail_clicked)
        self.tabs.addTab(self.thumbnails_list, "Thumbnails")

        self.bookmarks_tree = QTreeWidget()
        self.bookmarks_tree.setHeaderHidden(True)
        self.bookmarks_tree.itemClicked.connect(self._on_bookmark_clicked)
        self.tabs.addTab(self.bookmarks_tree, "Bookmarks")

    def show_thumbnails(self):
        self.tabs.setCurrentWidget(self.thumbnails_list)

    def show_bookmarks(self):
        self.tabs.setCurrentWidget(self.bookmarks_tree)

    def _on_thumbnail_clicked(self, item):
        page_num = item.data(Qt.ItemDataRole.UserRole)
        if page_num is not None:
            self.page_requested.emit(page_num)

    def _on_bookmark_clicked(self, item):
        page_num = item.data(0, Qt.ItemDataRole.UserRole)
        if page_num is not None:
            self.bookmark_requested.emit(page_num)

    def populate_from_document(self, doc, filepath):
        self.populate_thumbnails(filepath)
        self.populate_bookmarks(doc)

    def populate_thumbnails(self, filepath):
        self.thumbnails_list.clear()

        doc = fitz.open(filepath)
        for i in range(len(doc)):
            page = doc[i]
            mat = fitz.Matrix(0.2, 0.2)
            pix = page.get_pixmap(matrix=mat)

            fmt = QImage.Format.Format_RGBA8888 if pix.alpha else QImage.Format.Format_RGB888
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            qpixmap = QPixmap.fromImage(img)

            icon = QIcon(qpixmap)
            item = QListWidgetItem(icon, f"Page {i + 1}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.thumbnails_list.addItem(item)
        doc.close()

    def populate_bookmarks(self, doc):
        self.bookmarks_tree.clear()
        toc = doc.get_toc(simple=False) if doc else []
        if not toc:
            root = QTreeWidgetItem(["No bookmarks"])
            root.setData(0, Qt.ItemDataRole.UserRole, None)
            self.bookmarks_tree.addTopLevelItem(root)
            return

        parents = {0: None}
        for entry in toc:
            level = entry[0]
            title = entry[1]
            page_num = max(0, entry[2] - 1)
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, page_num)
            parent = parents.get(level - 1)
            if parent is None:
                self.bookmarks_tree.addTopLevelItem(item)
            else:
                parent.addChild(item)
            parents[level] = item
