import os
import sys

import fitz
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from render.engine import RenderEngine


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


def test_render_page(sample_pdf):
    engine = RenderEngine()
    engine.load_document(sample_pdf)
    pixmap = engine.render_page(0)
    assert pixmap is not None
    assert pixmap.width() > 0
    assert pixmap.height() > 0
    engine.close()
