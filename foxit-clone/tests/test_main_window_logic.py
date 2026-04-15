import os
import sys
from types import SimpleNamespace

import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ui.main_window import MainWindow


class FakeStatusBar:
    def __init__(self):
        self.messages = []

    def showMessage(self, message):
        self.messages.append(message)


class FakePdfView:
    def __init__(self):
        self.zoom_factor = 1.0
        self.rendered = []

    def set_pixmap(self, pixmap, zoom):
        self.rendered.append((pixmap, zoom))

    def map_ui_to_pdf(self, x, y, matrix):
        return fitz.Point(x, y)


class FakeSidebar:
    def __init__(self):
        self.calls = []

    def populate_from_document(self, doc, filepath):
        self.calls.append((len(doc), filepath))


class FakeAssistant:
    def __init__(self):
        self.messages = []

    def add_system_message(self, message):
        self.messages.append(message)


class FakeRenderer:
    def __init__(self):
        self.calls = []

    def request_render(self, page_num, zoom):
        self.calls.append((page_num, zoom))


def build_window(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(72, 72), "Hello Window", fontname="helv", fontsize=12)
    doc.save(str(pdf_path))
    doc.close()

    window = MainWindow()
    window.statusBar = lambda: FakeStatusBar()
    window.pdf_view = FakePdfView()
    window.sidebar = FakeSidebar()
    window.ai_assistant = FakeAssistant()
    window.renderer = FakeRenderer()
    window.filepath = str(pdf_path)
    window.engine.load_document(window.filepath)
    window.total_pages = window.engine.get_page_count()
    return window


def test_selected_rect_lookup(tmp_path):
    window = build_window(tmp_path)
    page = window.engine.doc[0]

    window.last_clicked_pdf_point = (75, 70)
    rect = window._selected_or_span_rect(page)

    assert rect is not None
    window.engine.close()


def test_set_status_records_message(tmp_path):
    window = build_window(tmp_path)
    status_bar = FakeStatusBar()
    window.statusBar = lambda: status_bar

    window._set_status("Ready for export")

    assert status_bar.messages[-1] == "Ready for export"
    assert window.ai_assistant.messages[-1] == "Ready for export"
    window.engine.close()


def test_replace_document_reloads_engine(tmp_path):
    window = build_window(tmp_path)

    replacement = tmp_path / "replacement.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.new_page()
    doc.save(str(replacement))
    doc.close()

    window._replace_document(str(replacement))

    assert window.filepath == str(replacement)
    assert window.total_pages == 2
    assert window.sidebar.calls
    assert window.renderer.calls
    window.engine.close()


def test_on_pdf_clicked_selects_text(tmp_path):
    window = build_window(tmp_path)
    window.statusBar = lambda: FakeStatusBar()

    window.on_pdf_clicked(75, 70)

    assert window.selected_rect is not None
    assert any("Selected text" in message for message in window.ai_assistant.messages)
    window.engine.close()


def test_on_zoom_requested_bounds_zoom(tmp_path):
    window = build_window(tmp_path)
    status_bar = FakeStatusBar()
    window.statusBar = lambda: status_bar

    window.on_zoom_requested(12.0)

    assert window.renderer.calls[-1] == (0, 5.0)
    assert status_bar.messages[-1] == "Zoom 5.00x"
    window.engine.close()


def test_on_page_requested_updates_status(tmp_path):
    window = build_window(tmp_path)
    status_bar = FakeStatusBar()
    window.statusBar = lambda: status_bar
    window.total_pages = 3
    window.current_page = 0

    window.on_page_requested(1)

    assert window.current_page == 1
    assert status_bar.messages[-1] == "Page 2 of 3"
    window.engine.close()
