from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QPushButton


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')
        self.setFixedSize(QSize(400, 300))
        self.setCentralWidget(QPushButton('Go!'))
