import pytest
import os
import sys
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from edit.text_editor import TextEditor

@pytest.fixture
def sample_page(tmp_path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "Hello World", fontname="helv", fontsize=12)
    pdf_path = tmp_path / "test_text.pdf"
    doc.save(str(pdf_path))
    doc.close()

    doc2 = fitz.open(str(pdf_path))
    yield doc2[0], doc2
    doc2.close()

def test_get_text_spans(sample_page):
    page, doc = sample_page
    editor = TextEditor(page)
    spans = editor.get_text_spans()

    assert len(spans) > 0
    assert "Hello World" in [s['text'] for s in spans]

def test_find_span_at_point(sample_page):
    page, doc = sample_page
    editor = TextEditor(page)
    span = editor.find_span_at_point((55, 45)) # inside bbox
    assert span is not None
    assert "Hello World" in span['text']

def test_redact_and_replace_text(sample_page):
    page, doc = sample_page
    editor = TextEditor(page)
    spans = editor.get_text_spans()
    target_span = spans[0]

    editor.redact_and_replace_text(target_span['bbox'], target_span['origin'], "Goodbye World", fontsize=12)

    new_text = page.get_text("text").strip()
    assert "Goodbye World" in new_text
    assert "Hello World" not in new_text
