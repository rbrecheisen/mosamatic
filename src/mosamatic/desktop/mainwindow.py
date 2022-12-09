import sys

import numpy as np
import pydicom

from PIL import Image, ImageQt
from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication, QPalette, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QSizePolicy


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
        self.scrollArea.setVisible(False)
        self.setCentralWidget(self.scrollArea)
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 5)
        self.load_and_set_image()

    def load_and_set_image(self):
        p = pydicom.dcmread('../resources/01_001.dcm')
        pixels = p.pixel_array.copy()
        minimum, maximum = np.min(pixels), np.max(pixels)
        pixels = (pixels - minimum) / (maximum - minimum)
        image = Image.fromarray(np.uint8(pixels * 255))
        image_qt = ImageQt.ImageQt(image)
        self.imageLabel.setPixmap(QPixmap.fromImage(image_qt))
        self.imageLabel.adjustSize()
        self.scrollArea.setVisible(True)


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
