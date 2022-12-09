import sys

import numpy as np
import pydicom

from PIL import Image, ImageQt
from PySide6.QtGui import QGuiApplication, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QSizePolicy, \
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton

from utils import DicomImage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')

        self.image = None
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)

        self.button = QPushButton('(400, 50)')
        self.button.clicked.connect(self.preset_selected)
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.button)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.scrollArea)
        self.main_layout.addLayout(self.button_layout)
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.resize(QGuiApplication.primaryScreen().availableSize() * 4 / 5)
        self.load_and_set_image()

    def load_and_set_image(self):
        self.image = DicomImage()
        self.update_image(self.image)

    def update_image(self, image):
        pixels = image.normalize_255(image.pixels)
        image = ImageQt.ImageQt(Image.fromarray(pixels))
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.imageLabel.adjustSize()
        self.imageLabel.update()

    def preset_selected(self):
        self.image.pixels = self.image.apply_window((400, 50), self.image.pixels)
        self.update_image(self.image)


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
