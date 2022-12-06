import sys


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel


def main():
    application = QApplication(sys.argv)
    label = QLabel('Hello, world')
    label.setAlignment(Qt.AlignCenter)
    label.setMinimumSize(300, 100)
    label.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
