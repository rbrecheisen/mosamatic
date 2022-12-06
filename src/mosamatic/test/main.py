import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QToolBar, QStatusBar
from PySide6.QtGui import QPalette, QColor, QAction, QIcon


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


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')
        self.setFixedSize(QSize(400, 300))
        label = QLabel('Hello!')
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
        toolbar = QToolBar('Toolbar')
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        action = QAction(Icon('bug.png'), 'Button', self)
        action.setStatusTip('This is a button')
        action.triggered.connect(self.on_action_triggered)
        toolbar.addAction(action)
        self.setStatusBar(QStatusBar(self))

    @staticmethod
    def on_action_triggered(s):
        print(f'click: {s}')


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
