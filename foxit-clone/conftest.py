import os
import sys
import types

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))


def _install_pyside6_stubs():
    if "PySide6" in sys.modules:
        return

    pyside6 = types.ModuleType("PySide6")
    qtcore = types.ModuleType("PySide6.QtCore")
    qtgui = types.ModuleType("PySide6.QtGui")
    qtwidgets = types.ModuleType("PySide6.QtWidgets")

    class BoundSignal:
        def __init__(self):
            self._callbacks = []

        def connect(self, callback):
            self._callbacks.append(callback)

        def emit(self, *args, **kwargs):
            for callback in list(self._callbacks):
                callback(*args, **kwargs)

    class Signal:
        def __init__(self, *args, **kwargs):
            self._name = None

        def __set_name__(self, owner, name):
            self._name = f"__signal_{name}"

        def __get__(self, instance, owner):
            if instance is None:
                return self
            signal = instance.__dict__.get(self._name)
            if signal is None:
                signal = BoundSignal()
                instance.__dict__[self._name] = signal
            return signal

    def Slot(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    class Qt:
        class ItemDataRole:
            UserRole = 32

        class Orientation:
            Horizontal = 1

        class KeyboardModifier:
            ControlModifier = 1

        class MouseButton:
            LeftButton = 1
            MiddleButton = 2

    class QSize:
        def __init__(self, width=0, height=0):
            self.width = width
            self.height = height

    class QMutex:
        pass

    class QMutexLocker:
        def __init__(self, mutex):
            self.mutex = mutex

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class QThread:
        def __init__(self):
            self._running = False

        def start(self):
            self._running = True

        def isRunning(self):
            return self._running

        def wait(self):
            self._running = False

    class QImage:
        class Format:
            Format_RGBA8888 = 1
            Format_RGB888 = 2

        def __init__(self, samples=None, width=0, height=0, stride=0, fmt=None):
            self._width = width
            self._height = height

        def width(self):
            return self._width

        def height(self):
            return self._height

    class QPixmap:
        def __init__(self, image=None, width=None, height=None):
            if isinstance(image, QImage):
                self._width = image.width()
                self._height = image.height()
            else:
                self._width = width or 0
                self._height = height or 0

        @classmethod
        def fromImage(cls, image):
            return cls(image=image)

        def isNull(self):
            return self._width == 0 or self._height == 0

        def width(self):
            return self._width

        def height(self):
            return self._height

    class QPixmapCache:
        _cache = {}

        @classmethod
        def setCacheLimit(cls, limit):
            cls._limit = limit

        @classmethod
        def find(cls, key):
            return cls._cache.get(key)

        @classmethod
        def insert(cls, key, value):
            cls._cache[key] = value

    class QWidget:
        def __init__(self, parent=None):
            self.parent = parent
            self._layout = None

        def setLayout(self, layout):
            self._layout = layout

    class QApplication:
        _instance = None

        def __init__(self, args=None):
            QApplication._instance = self

        @classmethod
        def instance(cls):
            return cls._instance

        def exec(self):
            return 0

    class QMainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.title = ""
            self.size = (0, 0)
            self.menu_widget = None
            self.central_widget = None

        def setWindowTitle(self, title):
            self.title = title

        def resize(self, width, height):
            self.size = (width, height)

        def setMenuWidget(self, widget):
            self.menu_widget = widget

        def setCentralWidget(self, widget):
            self.central_widget = widget

        def show(self):
            return None

    class QVBoxLayout:
        def __init__(self, parent=None):
            self.parent = parent
            self.items = []

        def addWidget(self, widget):
            self.items.append(widget)

        def setContentsMargins(self, *args):
            self.margins = args

    class QSplitter(QWidget):
        def __init__(self, orientation=None):
            super().__init__()
            self.widgets = []
            self.orientation = orientation

        def addWidget(self, widget):
            self.widgets.append(widget)

        def setSizes(self, sizes):
            self.sizes = sizes

    class QLabel(QWidget):
        def __init__(self, text=""):
            super().__init__()
            self._text = text

        def text(self):
            return self._text

        def setText(self, text):
            self._text = text

    class QTextEdit(QWidget):
        def __init__(self):
            super().__init__()
            self._text = ""
            self._read_only = False

        def setReadOnly(self, value):
            self._read_only = value

        def append(self, text):
            self._text = f"{self._text}\n{text}".strip()

        def toPlainText(self):
            return self._text

    class QLineEdit(QWidget):
        def __init__(self):
            super().__init__()
            self._text = ""
            self._placeholder = ""

        def setPlaceholderText(self, text):
            self._placeholder = text

        def setText(self, text):
            self._text = text

        def text(self):
            return self._text

        def clear(self):
            self._text = ""

    class QPushButton(QWidget):
        clicked = Signal()

        def __init__(self, text=""):
            super().__init__()
            self.text = text

        def click(self):
            self.clicked.emit()

    class QListWidgetItem:
        def __init__(self, icon=None, text=""):
            self.icon = icon
            self.text = text
            self._data = {}

        def setData(self, role, value):
            self._data[role] = value

        def data(self, role):
            return self._data.get(role)

    class QListWidget(QWidget):
        itemClicked = Signal(object)

        def __init__(self):
            super().__init__()
            self.items = []
            self.icon_size = None

        def setIconSize(self, size):
            self.icon_size = size

        def addItem(self, item):
            self.items.append(item)

        def clear(self):
            self.items = []

        def count(self):
            return len(self.items)

    class QTreeWidgetItem:
        def __init__(self, texts=None):
            self.texts = texts or []
            self.children = []
            self._data = {}

        def setData(self, column, role, value):
            self._data[(column, role)] = value

        def data(self, column, role):
            return self._data.get((column, role))

        def addChild(self, child):
            self.children.append(child)

    class QTreeWidget(QWidget):
        itemClicked = Signal(object)

        def __init__(self):
            super().__init__()
            self.items = []
            self.header_hidden = False

        def setHeaderHidden(self, hidden):
            self.header_hidden = hidden

        def clear(self):
            self.items = []

        def addTopLevelItem(self, item):
            self.items.append(item)

    class QTabWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.tabs = []
            self.current = None

        def addTab(self, widget, title):
            self.tabs.append((widget, title))
            if self.current is None:
                self.current = widget

        def count(self):
            return len(self.tabs)

        def tabText(self, index):
            return self.tabs[index][1]

        def setCurrentWidget(self, widget):
            self.current = widget

    class QIcon:
        def __init__(self, pixmap=None):
            self.pixmap = pixmap

    class QFileDialog:
        @staticmethod
        def getOpenFileName(*args, **kwargs):
            return "", ""

        @staticmethod
        def getSaveFileName(*args, **kwargs):
            return "", ""

    class QInputDialog:
        @staticmethod
        def getText(*args, **kwargs):
            return "", False

    class QMessageBox:
        @staticmethod
        def information(*args, **kwargs):
            return 0

        @staticmethod
        def warning(*args, **kwargs):
            return 0

    class QGraphicsScene:
        def __init__(self, parent=None):
            self.parent = parent
            self.items = []

        def addItem(self, item):
            self.items.append(item)

        def setSceneRect(self, rect):
            self.rect = rect

    class QGraphicsPixmapItem:
        def __init__(self):
            self._pixmap = QPixmap()

        def setPixmap(self, pixmap):
            self._pixmap = pixmap

        def boundingRect(self):
            return (0, 0, self._pixmap.width(), self._pixmap.height())

    class QGraphicsView(QWidget):
        class DragMode:
            ScrollHandDrag = 1
            NoDrag = 0

        def __init__(self, parent=None):
            super().__init__(parent)
            self._scene = None
            self._drag_mode = self.DragMode.NoDrag

        def setScene(self, scene):
            self._scene = scene

        def scene(self):
            return self._scene

        def setRenderHint(self, hint):
            self.hint = hint

        def renderHints(self):
            return 0

        def resetTransform(self):
            return None

        def setDragMode(self, mode):
            self._drag_mode = mode

        def mapToScene(self, x, y=None):
            if y is None:
                point = x
                return types.SimpleNamespace(x=lambda: point.x(), y=lambda: point.y())
            return types.SimpleNamespace(x=lambda: x, y=lambda: y)

        def wheelEvent(self, event):
            return None

        def mousePressEvent(self, event):
            return None

        def mouseReleaseEvent(self, event):
            return None

    qtcore.Signal = Signal
    qtcore.Slot = Slot
    qtcore.Qt = Qt
    qtcore.QSize = QSize
    qtcore.QThread = QThread
    qtcore.QMutex = QMutex
    qtcore.QMutexLocker = QMutexLocker

    qtgui.QImage = QImage
    qtgui.QPixmap = QPixmap
    qtgui.QPixmapCache = QPixmapCache
    qtgui.QIcon = QIcon
    qtgui.QAction = object

    qtwidgets.QWidget = QWidget
    qtwidgets.QApplication = QApplication
    qtwidgets.QMainWindow = QMainWindow
    qtwidgets.QVBoxLayout = QVBoxLayout
    qtwidgets.QSplitter = QSplitter
    qtwidgets.QLabel = QLabel
    qtwidgets.QTextEdit = QTextEdit
    qtwidgets.QLineEdit = QLineEdit
    qtwidgets.QPushButton = QPushButton
    qtwidgets.QListWidget = QListWidget
    qtwidgets.QListWidgetItem = QListWidgetItem
    qtwidgets.QTreeWidget = QTreeWidget
    qtwidgets.QTreeWidgetItem = QTreeWidgetItem
    qtwidgets.QTabWidget = QTabWidget
    qtwidgets.QFileDialog = QFileDialog
    qtwidgets.QInputDialog = QInputDialog
    qtwidgets.QMessageBox = QMessageBox
    qtwidgets.QGraphicsView = QGraphicsView
    qtwidgets.QGraphicsScene = QGraphicsScene
    qtwidgets.QGraphicsPixmapItem = QGraphicsPixmapItem

    pyside6.QtCore = qtcore
    pyside6.QtGui = qtgui
    pyside6.QtWidgets = qtwidgets

    sys.modules["PySide6"] = pyside6
    sys.modules["PySide6.QtCore"] = qtcore
    sys.modules["PySide6.QtGui"] = qtgui
    sys.modules["PySide6.QtWidgets"] = qtwidgets


try:
    import importlib.util

    pyside6_spec = importlib.util.find_spec("PySide6")
    if pyside6_spec is None:
        raise ImportError
    raise ImportError
except ImportError:
    _install_pyside6_stubs()
    from PySide6.QtWidgets import QApplication

import pytest


@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
