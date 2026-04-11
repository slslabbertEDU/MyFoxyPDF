from PySide6.QtCore import QThread, Signal
from .engine import RenderEngine

class RenderRequest:
    def __init__(self, page_num, zoom):
        self.page_num = page_num
        self.zoom = zoom

class AsyncRenderer(QThread):
    render_completed = Signal(int, object)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.queue = []
        self._is_running = True

    def request_render(self, page_num, zoom=1.0):
        self.queue.append(RenderRequest(page_num, zoom))
        if not self.isRunning():
            self.start()

    def run(self):
        while self.queue and self._is_running:
            req = self.queue.pop(0)
            pixmap = self.engine.render_page(req.page_num, req.zoom)
            if pixmap:
                self.render_completed.emit(req.page_num, pixmap)

    def stop(self):
        self._is_running = False
        self.queue.clear()
        self.wait()
