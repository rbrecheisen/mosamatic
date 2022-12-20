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

    def __init__(self, file_path='../resources/example.dcm'):
        self.file_path = file_path
        self.pixels = self.load()

    def load(self):
        p = pydicom.dcmread(self.file_path)
        self.pixels = p.pixel_array.copy()
        self.pixels = self.pixels.reshape(p.Rows, p.Columns)
        self.pixels = p.RescaleSlope * self.pixels + p.RescaleIntercept
        return self.pixels

    @staticmethod
    def normalize(pixels):
        minimum, maximum = np.min(pixels), np.max(pixels)
        pixels = (pixels + np.abs(minimum)) / (maximum - minimum)
        return pixels

    @staticmethod
    def normalize_255(pixels):
        pixels = DicomImage.normalize(pixels)
        pixels = np.uint8(pixels * 255)
        return pixels

    @staticmethod
    def apply_window(window, pixels):
        pixels = (pixels - window[1] + 0.5 * window[0]) / window[0]
        pixels[pixels < 0] = 0
        pixels[pixels > 1] = 1
        return pixels
