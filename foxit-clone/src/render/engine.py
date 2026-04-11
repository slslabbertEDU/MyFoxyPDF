import fitz
from PySide6.QtGui import QPixmap, QImage

class RenderEngine:
    def __init__(self):
        self.doc = None

    def load_document(self, path):
        self.doc = fitz.open(path)

    def get_page_count(self):
        if self.doc:
            return len(self.doc)
        return 0

    def render_page(self, page_index, zoom=1.0):
        if not self.doc or page_index < 0 or page_index >= len(self.doc):
            return QPixmap()

        page = self.doc[page_index]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Convert fitz pixmap to QImage
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        qt_img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)

        return QPixmap.fromImage(qt_img)

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None
