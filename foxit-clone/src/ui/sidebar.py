from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QListWidget, QTreeWidget, QListWidgetItem
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QImage
import fitz

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
        self.thumbnails_list.setIconSize(QSize(100, 150))
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

    def populate_thumbnails(self, filepath):
        """Generates actual low-res thumbnail pixmaps from the PDF."""
        self.thumbnails_list.clear()

        doc = fitz.open(filepath)
        for i in range(len(doc)):
            page = doc[i]
            # Use small matrix for quick thumbnail generation
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
