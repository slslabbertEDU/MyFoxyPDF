from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

class PDFView(QGraphicsView):
    zoom_requested = Signal(float)
    click_requested = Signal(float, float) # UI x, y
    rubberband_selected = Signal(float, float, float, float) # x, y, w, h

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(self.renderHints())

        self.current_item = QGraphicsPixmapItem()
        self.scene.addItem(self.current_item)
        self.zoom_factor = 1.0

    def set_pixmap(self, pixmap: QPixmap, zoom: float):
        self.current_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.current_item.boundingRect())

        # Reset view scale since the pixmap itself is now rendered at the correct resolution
        self.resetTransform()
        self.zoom_factor = zoom

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_factor *= 1.2
            else:
                self.zoom_factor /= 1.2

            self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))

            # Emit signal to request a high-res re-render from the engine
            self.zoom_requested.emit(self.zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            fake_event = event.clone()
            super().mousePressEvent(fake_event)
        elif event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.position().toPoint())
            self.click_requested.emit(pos.x(), pos.y())
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

        # Capture rubber band geometry before super() clears it
        is_rubber_band = self.dragMode() == QGraphicsView.DragMode.RubberBandDrag
        rect = self.rubberBandRect()
        valid_rect = is_rubber_band and rect.isValid() and not rect.isEmpty()

        if valid_rect:
            top_left = self.mapToScene(rect.topLeft())
            bottom_right = self.mapToScene(rect.bottomRight())

        super().mouseReleaseEvent(event)

        if valid_rect:
            self.rubberband_selected.emit(
                top_left.x(),
                top_left.y(),
                bottom_right.x() - top_left.x(),
                bottom_right.y() - top_left.y()
            )

    def map_ui_to_pdf(self, ui_x, ui_y, page_matrix):
        """
        Maps a UI pixel coordinate to a PDF document point
        using the inverse transformation matrix as required by specs.
        """
        import fitz

        # Adjust for any view scaling
        scene_point = self.mapToScene(ui_x, ui_y)

        pdf_point = fitz.Point(scene_point.x(), scene_point.y())
        inverted_matrix = ~page_matrix
        return pdf_point * inverted_matrix
