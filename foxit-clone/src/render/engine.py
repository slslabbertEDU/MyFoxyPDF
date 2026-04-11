import fitz
from PySide6.QtGui import QImage, QPixmap

class RenderEngine:
    def __init__(self):
        self.doc = None

    def load_document(self, filepath):
        self.doc = fitz.open(filepath)

    def get_page_count(self):
        return len(self.doc) if self.doc else 0

    def render_page(self, page_num, zoom=1.0):
        if not self.doc or page_num < 0 or page_num >= len(self.doc):
            return None

        page = self.doc[page_num]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        fmt = QImage.Format.Format_RGBA8888 if pix.alpha else QImage.Format.Format_RGB888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        return QPixmap.fromImage(img)

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None
