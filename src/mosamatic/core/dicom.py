import os
import pydicom
import pydicom.errors
import numpy as np


class DicomImage:

    def __init__(self, file_path='../resources/example.dcm', rescale=True):
        self.file_path = file_path
        self.pixels = self.load(rescale)

    def load(self, rescale):
        try:
            p = pydicom.dcmread(self.file_path)
            pixels = p.pixel_array.copy()
            pixels = pixels.reshape(p.Rows, p.Columns)
            if rescale:
                pixels = p.RescaleSlope * pixels + p.RescaleIntercept
            return pixels
        except pydicom.errors.InvalidDicomError:
            return None

    @staticmethod
    def normalize(pixels):
        minimum, maximum = np.min(pixels), np.max(pixels)
        pixels = (pixels + np.abs(minimum)) / (maximum - minimum)
        return pixels

    @staticmethod
    def normalize_0_255(pixels):
        pixels = DicomImage.normalize(pixels)
        pixels = np.uint8(pixels * 255)
        return pixels

    @staticmethod
    def apply_window(window, pixels):
        pixels = (pixels - window[1] + 0.5 * window[0]) / window[0]
        pixels[pixels < 0] = 0
        pixels[pixels > 1] = 1
        return pixels


class DicomImageLoader:

    def __init__(self, dir_path, rescale=True):
        self.dir_path = dir_path
        self.images = self.load(rescale=rescale)

    def load(self, rescale):
        images = []
        for f in os.listdir(self.dir_path):
            f_path = os.path.join(self.dir_path, f)
            image = DicomImage(f_path, rescale)
            if image is not None:
                images = image
                print(f'Loaded {f_path}')
        return images
