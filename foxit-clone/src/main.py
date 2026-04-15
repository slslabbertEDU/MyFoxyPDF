import os
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MyFoxyPDF")
    app.setOrganizationName("MyFoxyPDF")

    try:
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as exc:
        QMessageBox.critical(None, "Startup error", str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
