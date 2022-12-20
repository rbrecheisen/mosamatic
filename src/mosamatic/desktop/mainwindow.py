import sys

from PIL import Image, ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QSizePolicy, \
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QSpacerItem


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
