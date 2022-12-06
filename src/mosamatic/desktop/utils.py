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
