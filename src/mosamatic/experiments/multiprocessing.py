import sys
import time
import traceback

from PySide6.QtCore import QSize, QTimer, QRunnable, Slot, QThreadPool, QObject, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel, QVBoxLayout


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosamatic Desktop')
        self.setFixedSize(QSize(400, 300))
        self.counter = 0
        layout = QVBoxLayout()
        self.label = QLabel('Start')
        button = QPushButton('DANGER!')
        button.pressed.connect(self.oh_no)
        layout.addWidget(self.label)
        layout.addWidget(button)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        self.threadpool = QThreadPool()

    @staticmethod
    def worker_function(progress_callback):
        for n in range(5):
            time.sleep(1)
            progress_callback.emit(n * 100/4)
        return 'Done'

    @staticmethod
    def print_output(s):
        print(s)

    @staticmethod
    def thread_complete():
        print('THREAD COMPLETE!')

    @staticmethod
    def print_progress(n):
        print(f'{n} done')

    def oh_no(self):
        worker = Worker(self.worker_function)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.print_progress)
        self.threadpool.start(worker)

    def recurring_timer(self):
        self.counter += 1
        self.label.setText(f'Counter: {self.counter}')


def main():
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()
