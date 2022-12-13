import sys

from PIL import Image, ImageQt
from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QPixmap, QTransform

from utils import DicomImage


# TODO: Implement separate states for zooming (Z) and panning (P)
class GraphicsView(QGraphicsView):

    def __init__(self, scene):
        super().__init__(scene)
        self.setDragMode(GraphicsView.DragMode.ScrollHandDrag)  # move this to set_state()

    def wheelEvent(self, event):
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        old_pos = self.mapToScene(event.position().toPoint())
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            self.setTransform(QTransform())


def main():
    application = QApplication(sys.argv)
    scene = QGraphicsScene(0, 0, 800, 600)
    image = DicomImage()
    pixels = image.apply_window((400, 50), image.pixels)
    pixels = DicomImage.normalize_255(pixels)
    pixmap_image = ImageQt.ImageQt(Image.fromarray(pixels))
    scene_item = scene.addPixmap(QPixmap.fromImage(pixmap_image))
    scene_item.setPos(0, 0)
    view = GraphicsView(scene)
    view.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
