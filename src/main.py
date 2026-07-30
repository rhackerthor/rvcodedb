import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VisualDecoder")

    font = QFont("JetBrains Mono", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
