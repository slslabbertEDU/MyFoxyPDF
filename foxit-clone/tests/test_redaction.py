import pytest
import os
import sys
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from security.redaction import apply_redaction

def test_apply_redaction(tmp_path):
    pdf_path = tmp_path / "test_redact.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "TOP SECRET DATA", fontname="helv", fontsize=12)

    apply_redaction(page, (40, 30, 200, 60))

    doc.save(str(pdf_path))
    doc.close()

    doc2 = fitz.open(str(pdf_path))
    page2 = doc2[0]
    extracted = page2.get_text("text").strip()

    assert "SECRET" not in extracted
    doc2.close()
