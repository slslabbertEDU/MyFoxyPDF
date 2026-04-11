import pytest
import os
import sys
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ui.sidebar import Sidebar

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def test_sidebar_initialization(qapp):
    sidebar = Sidebar()
    assert sidebar.tabs.count() == 2
    assert sidebar.tabs.tabText(0) == "Thumbnails"
    assert sidebar.tabs.tabText(1) == "Bookmarks"

def test_sidebar_populate_thumbnails(qapp):
    sidebar = Sidebar()
    sidebar.populate_thumbnails(5)
    assert sidebar.thumbnails_list.count() == 5
