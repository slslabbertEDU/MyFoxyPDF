import os
import sys

import fitz
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from ui.sidebar import Sidebar


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    for _ in range(5):
        doc.new_page()
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


def test_sidebar_initialization():
    sidebar = Sidebar()
    assert sidebar.tabs.count() == 2
    assert sidebar.tabs.tabText(0) == "Thumbnails"
    assert sidebar.tabs.tabText(1) == "Bookmarks"


def test_sidebar_populate_thumbnails(sample_pdf):
    sidebar = Sidebar()
    sidebar.populate_thumbnails(sample_pdf)
    assert sidebar.thumbnails_list.count() == 5
