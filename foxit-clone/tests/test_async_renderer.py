import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from render.async_renderer import AsyncRenderer


class FakeEngine:
    def render_page(self, page_num, zoom):
        return {"page": page_num, "zoom": zoom}


def test_cache_key_format():
    assert AsyncRenderer._cache_key(2, 1.234) == "2_1.23"


def test_request_render_queues_latest_page():
    renderer = AsyncRenderer(FakeEngine())
    renderer.start = lambda: None

    renderer.request_render(1, 1.0)
    renderer.request_render(1, 2.0)

    assert len(renderer.queue) == 1
    assert renderer.queue[0].page_num == 1
    assert renderer.queue[0].zoom == 2.0
