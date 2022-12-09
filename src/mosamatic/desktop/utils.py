import pydicom
import numpy as np

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon, QPalette, QColor


class Icon(QIcon):
    def __init__(self, name):
        super().__init__(f'../resources/icons/{name}')


class ColoredWidget(QWidget):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class DicomImage:

    def __init__(self, file_path):
        self.file_path = file_path
        self.pixels = None
        self.load()

    def load(self):
        p = pydicom.dcmread(self.file_path)
        self.pixels = p.pixel_array.copy()

    def get_pixels(self):
        return self.pixels

    def get_pixels_normalized(self):
        minimum, maximum = np.min(self.pixels), np.max(self.pixels)
        pixels = (self.pixels + np.abs(minimum)) / (maximum - minimum)
        return pixels

    def get_pixels_normalized_255(self):
        pixels = self.get_pixels_normalized()
        return np.uint8(pixels * 255)
