from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
from PySide6.QtGui import QPixmapCache
import time

class RenderRequest:
    def __init__(self, page_num, zoom):
        self.page_num = page_num
        self.zoom = zoom
        self.timestamp = time.time()

class AsyncRenderer(QThread):
    render_completed = Signal(int, float, object) # page_num, zoom, QPixmap

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.queue = []
        self._is_running = True
        self.mutex = QMutex()

        # Enforce 500MB QPixmapCache limit as per instructions
        QPixmapCache.setCacheLimit(500 * 1024)

    def request_render(self, page_num, zoom=1.0):
        cache_key = f"{page_num}_{zoom:.2f}"
        if QPixmapCache.find(cache_key):
            # Already cached
            return

        with QMutexLocker(self.mutex):
            # Cancel outdated requests for the same page
            self.queue = [req for req in self.queue if req.page_num != page_num]
            self.queue.append(RenderRequest(page_num, zoom))
            # Sort by most recent first to prioritize newest zoom actions
            self.queue.sort(key=lambda x: x.timestamp, reverse=True)

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
                    cache_key = f"{req.page_num}_{req.zoom:.2f}"
                    QPixmapCache.insert(cache_key, pixmap)
                    self.render_completed.emit(req.page_num, req.zoom, pixmap)
            else:
                time.sleep(0.01) # Avoid busy wait

    def stop(self):
        self._is_running = False
        with QMutexLocker(self.mutex):
            self.queue.clear()
        self.wait()
