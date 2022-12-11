import sys

from PIL import Image, ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QSizePolicy, \
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QSpacerItem

from utils import DicomImage


class MainWindow(QMainWindow):

    NORMAL = 0
    ZOOM = 1
    PAN = 2
    DEFAULT = NORMAL

    STATUS_MESSAGES = {
        NORMAL: 'Status: NORMAL',
        ZOOM: 'Status: ZOOM',
        PAN: 'Status: PAN',
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')
        self.image = None
        self.scaleFactor = 1.0
        self.status = None
        self.previous_state = None
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.buttonPreset = QPushButton('(400, 50)')
        self.buttonPreset.clicked.connect(self.preset_selected)
        self.buttonZoomOut = QPushButton('Zoom -')
        self.buttonZoomOut.clicked.connect(self.zoom_out)
        self.buttonZoomIn = QPushButton('Zoom + ')
        self.buttonZoomIn.clicked.connect(self.zoom_in)
        self.buttonZoomReset = QPushButton('100%')
        self.buttonZoomReset.clicked.connect(self.zoom_reset)
        self.buttonZoomFitWindow = QPushButton('Fit window')
        self.buttonZoomFitWindow.clicked.connect(self.zoom_fit_window)
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.buttonPreset)
        self.button_layout.addWidget(self.buttonZoomOut)
        self.button_layout.addWidget(self.buttonZoomIn)
        self.button_layout.addWidget(self.buttonZoomReset)
        self.button_layout.addWidget(self.buttonZoomFitWindow)
        self.button_layout.addItem(QSpacerItem(1, 1, QSizePolicy.Preferred, QSizePolicy.Expanding))
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.scrollArea)
        self.main_layout.addLayout(self.button_layout)
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.available_size = QGuiApplication.primaryScreen().availableSize()
        self.resize(self.available_size)
        self.set_status(MainWindow.DEFAULT)
        self.load_image()

    def set_status(self, status):
        self.previous_state = self.status
        self.status = status
        status_text = MainWindow.STATUS_MESSAGES[self.status]
        if self.previous_state is not None and self.status != MainWindow.NORMAL:
            status_text += ' (previous: {})'.format(MainWindow.STATUS_MESSAGES[self.previous_state])
        self.statusBar().showMessage(status_text)

    def load_image(self):
        self.image = DicomImage()
        self.update_image_display(self.image)

    def update_image_display(self, image):
        pixels = DicomImage.normalize_255(image.pixels)
        image = ImageQt.ImageQt(Image.fromarray(pixels))
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.imageLabel.adjustSize()
        self.imageLabel.update()

    def preset_selected(self):
        self.image.pixels = self.image.apply_window((400, 50), self.image.pixels)
        self.update_image_display(self.image)

    def zoom_in(self):
        self.scale_image(1.2)

    def zoom_out(self):
        self.scale_image(0.8)

    def zoom_reset(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def zoom_fit_window(self):
        factor = self.available_size.height() / float(self.imageLabel.height())
        self.scale_image(factor)

    def scale_image(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())
        self.adjust_scrollbar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjust_scrollbar(self.scrollArea.verticalScrollBar(), factor)

    @staticmethod
    def adjust_scrollbar(scrollbar, factor):
        scrollbar.setValue(int(factor * scrollbar.value() + ((factor - 1) * scrollbar.pageStep() / 2)))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            self.set_status(MainWindow.NORMAL)
        elif event.key() == Qt.Key.Key_N:
            self.set_status(MainWindow.NORMAL)
        elif event.key() == Qt.Key.Key_Z:
            self.set_status(MainWindow.ZOOM)
        elif event.key() == Qt.Key.Key_P:
            self.set_status(MainWindow.PAN)
        else:
            pass

    def mouseReleaseEvent(self, event):
        # Get mouse coordinates
        pass


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
