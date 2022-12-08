import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter

COLORS = [
    # 17 undertones https://lospec.com/palette-list/17undertones
    '#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
    '#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
    '#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',
]


class Icon(QIcon):

    def __init__(self, name):
        super().__init__(f'../resources/{name}')


class ColoredWidget(QWidget):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class Canvas(QLabel):

    def __init__(self, w, h):
        super().__init__()
        pixmap = QPixmap(w, h)
        self.setPixmap(pixmap)
        self.last_x, self.last_y = None, None
        self.pen_color = QColor('#000000')

    def set_pen_color(self, color):
        self.pen_color = color

    def mouseMoveEvent(self, e):
        # Mouse tracking is False by default so this method is only called
        # when the user presses the mouse button first!
        x = e.position().x()
        y = e.position().y()
        if self.last_x is None:
            self.last_x = x
            self.last_y = y
            return
        canvas = self.pixmap()
        painter = QPainter(canvas)
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, x, y)
        painter.end()
        self.setPixmap(canvas)
        self.last_x = x
        self.last_y = y

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None


class PaletteButton(QPushButton):

    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QSize(24, 24))
        self.color = color
        self.setStyleSheet(f'background-color: {color}')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')
        self.setFixedSize(QSize(400, 300))
        self.canvas = Canvas(400, 300)
        palette = QHBoxLayout()
        self.add_palette_buttons(palette)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(palette)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

    def add_palette_buttons(self, layout):
        for color in COLORS:
            button = PaletteButton(color)
            button.pressed.connect(lambda c=color: self.canvas.set_pen_color(c))
            layout.addWidget(button)


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
