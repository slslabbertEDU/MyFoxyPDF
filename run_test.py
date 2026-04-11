import sys
import os
import fitz
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath('foxit-clone/src'))
from render.engine import RenderEngine

def main():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    engine = RenderEngine()
    print("Engine created")

    # create sample pdf
    doc = fitz.open()
    doc.new_page()
    doc.save("sample.pdf")
    doc.close()

    engine.load_document("sample.pdf")
    print("Page count:", engine.get_page_count())

    pixmap = engine.render_page(0)
    print("Pixmap valid:", not pixmap.isNull())

    engine.close()
    os.remove("sample.pdf")

if __name__ == '__main__':
    main()
