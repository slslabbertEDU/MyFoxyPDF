import fitz
from PySide6.QtGui import QImage, QPixmap

class RenderEngine:
    def __init__(self):
        self.doc = None

    def load_document(self, filepath: str):
        self.doc = fitz.open(filepath)

    def get_page_count(self) -> int:
        if self.doc:
            return len(self.doc)
        return 0

    def render_page(self, page_index: int, zoom: float = 1.0) -> QPixmap:
        if not self.doc or page_index < 0 or page_index >= len(self.doc):
            return QPixmap()

        page = self.doc[page_index]
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)

        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        return QPixmap.fromImage(image)

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None
