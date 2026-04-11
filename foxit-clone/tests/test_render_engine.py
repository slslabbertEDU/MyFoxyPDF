import pytest
import os
import fitz
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from render.engine import RenderEngine

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_load_document(sample_pdf):
    engine = RenderEngine()
    engine.load_document(sample_pdf)
    assert engine.get_page_count() == 1
    engine.close()

def test_render_page(qapp, sample_pdf):
    engine = RenderEngine()
    engine.load_document(sample_pdf)
    pixmap = engine.render_page(0)
    assert isinstance(pixmap, QPixmap)
    assert not pixmap.isNull()
    engine.close()
