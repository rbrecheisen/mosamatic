import sys

from PIL import Image, ImageQt
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QPixmap

from utils import DicomImage


def main():
    application = QApplication(sys.argv)
    scene = QGraphicsScene(0, 0, 800, 600)
    image = DicomImage()
    pixels = image.apply_window((400, 50), image.pixels)
    pixels = DicomImage.normalize_255(pixels)
    pixmap_image = ImageQt.ImageQt(Image.fromarray(pixels))
    scene_item = scene.addPixmap(QPixmap.fromImage(pixmap_image))
    scene_item.setPos(0, 0)
    view = QGraphicsView(scene)
    view.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
