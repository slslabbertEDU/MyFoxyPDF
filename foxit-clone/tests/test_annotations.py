import pytest
import os
import sys
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from edit.annotations import add_highlight

def test_add_highlight(tmp_path):
    pdf_path = tmp_path / "test_annot.pdf"
    doc = fitz.open()
    page = doc.new_page()

    rect = (50, 50, 200, 100)
    add_highlight(page, rect)

    doc.save(str(pdf_path))
    doc.close()

    doc2 = fitz.open(str(pdf_path))
    page2 = doc2[0]

    annots = list(page2.annots())
    assert len(annots) == 1
    assert annots[0].type[0] == fitz.PDF_ANNOT_HIGHLIGHT
    doc2.close()
