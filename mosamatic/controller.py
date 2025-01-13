from mosamatic.processing import Processing
from mosamatic.view import View


class Controller:
    def __init__(self, root):
        self.processing, self.view = Processing(root), View(root, self)

    def start_task(self):
        self.processing.run_task(self.on_progress)

    def on_progress(self, progress):
        self.view.update_progress(progress)
