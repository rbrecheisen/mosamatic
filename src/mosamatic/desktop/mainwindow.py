import sys

import numpy as np
import pydicom

from PIL import Image, ImageQt
from PySide6.QtGui import QGuiApplication, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QSizePolicy

from utils import DicomImage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)
        self.setCentralWidget(self.scrollArea)
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 5)
        self.load_and_set_image()

    def load_and_set_image(self):
        dcm_image = DicomImage()
        dcm_image.apply_window((400, 50))  # TODO: create window presets!
        pixels = dcm_image.normalize_255()
        image = ImageQt.ImageQt(Image.fromarray(pixels))
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.imageLabel.adjustSize()
        self.scrollArea.setVisible(True)


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
