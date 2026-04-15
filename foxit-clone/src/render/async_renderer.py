import time

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal
from PySide6.QtGui import QPixmapCache


class RenderRequest:
    def __init__(self, page_num, zoom):
        self.page_num = page_num
        self.zoom = zoom
        self.timestamp = time.time()


class AsyncRenderer(QThread):
    render_completed = Signal(int, float, object)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.queue = []
        self._is_running = True
        self.mutex = QMutex()

        QPixmapCache.setCacheLimit(500 * 1024)

    def request_render(self, page_num, zoom=1.0):
        cache_key = self._cache_key(page_num, zoom)
        cached_pixmap = QPixmapCache.find(cache_key)
        if cached_pixmap:
            self.render_completed.emit(page_num, zoom, cached_pixmap)
            return

        with QMutexLocker(self.mutex):
            self.queue = [req for req in self.queue if req.page_num != page_num]
            self.queue.append(RenderRequest(page_num, zoom))
            self.queue.sort(key=lambda request: request.timestamp, reverse=True)

        if not self.isRunning():
            self.start()

    def run(self):
        while self._is_running:
            req = None
            with QMutexLocker(self.mutex):
                if self.queue:
                    req = self.queue.pop(0)

            if req:
                pixmap = self.engine.render_page(req.page_num, req.zoom)
                if pixmap:
                    QPixmapCache.insert(self._cache_key(req.page_num, req.zoom), pixmap)
                    self.render_completed.emit(req.page_num, req.zoom, pixmap)
            else:
                time.sleep(0.01)

    def stop(self):
        self._is_running = False
        with QMutexLocker(self.mutex):
            self.queue.clear()
        self.wait()

    @staticmethod
    def _cache_key(page_num, zoom):
        return f"{page_num}_{zoom:.2f}"
