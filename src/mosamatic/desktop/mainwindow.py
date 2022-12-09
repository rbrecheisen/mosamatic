from PySide6.QtCore import QSize, QStandardPaths, QDir
from PySide6.QtGui import QGuiApplication, QPalette, QAction
from PySide6.QtWidgets import QMainWindow, QDialog, QFileDialog, QScrollArea, QLabel, QSizePolicy


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')
        self.setFixedSize(QSize(400, 300))
        self.image = None
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)
        self.setCentralWidget(self.scrollArea)
        self.create_actions()
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 5)
        self.first_dialog = True

    def init_file_dialog(self, dialog, accept_mode):
        if self.first_dialog:
            self.first_dialog = False
            pictures_locations = QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)
            dialog.setDirectory(pictures_locations.isEmpty() if QDir.currentPath() else pictures_locations)
        mime_type_filters = None


    def on_open(self):
        pass

    def on_save(self):
        pass

    def on_exit(self):
        pass

    def on_zoom_in(self):
        pass

    def on_zoom_out(self):
        pass

    def on_norm(self):
        pass

    def on_fit_window(self):
        pass

    def create_actions(self):
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.on_open)
        save_action = QAction('Save as', self)
        save_action.triggered.connect(self.on_save)
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.on_exit)
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        zoom_in_action = QAction('Zoom in', self)
        zoom_in_action.triggered.connect(self.on_zoom_in)
        zoom_in_action.setEnabled(False)
        zoom_out_action = QAction('Zoom out', self)
        zoom_out_action.triggered.connect(self.on_zoom_out)
        zoom_out_action.setEnabled(False)
        norm_action = QAction('Normal size', self)
        norm_action.triggered.connect(self.on_norm)
        norm_action.setEnabled(False)
        fit_window_action = QAction('Fit to window', self)
        fit_window_action.triggered.connect(self.on_fit_window)
        fit_window_action.setEnabled(False)
        fit_window_action.setCheckable(True)
        view_menu = self.menuBar().addMenu('View')
        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)
        view_menu.addAction(norm_action)
        view_menu.addSeparator()
        view_menu.addAction(fit_window_action)
