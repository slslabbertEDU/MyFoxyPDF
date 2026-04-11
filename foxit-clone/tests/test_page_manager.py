import pytest
import os
import sys
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from edit.page_manager import PageManager

@pytest.fixture
def empty_doc():
    return fitz.open()

def test_insert_page(empty_doc):
    pm = PageManager(empty_doc)
    pm.insert_empty_page()
    assert len(empty_doc) == 1

def test_delete_page(empty_doc):
    empty_doc.new_page()
    pm = PageManager(empty_doc)
    assert pm.delete_page(0) == True
    assert len(empty_doc) == 0

def test_rotate_page(empty_doc):
    empty_doc.new_page()
    pm = PageManager(empty_doc)
    pm.rotate_page(0, 90)
    assert empty_doc[0].rotation == 90

def test_merge_pdf(tmp_path):
    doc1 = fitz.open()
    doc1.new_page()

    doc2_path = tmp_path / "doc2.pdf"
    doc2 = fitz.open()
    doc2.new_page()
    doc2.save(str(doc2_path))
    doc2.close()

    pm = PageManager(doc1)
    pm.merge_pdf(str(doc2_path))
    assert len(doc1) == 2
    doc1.close()
