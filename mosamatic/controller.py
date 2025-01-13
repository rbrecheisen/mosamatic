from model import AppModel
from view import AppView


class AppController:
    def __init__(self, root):
        self.model, self.view = AppModel(root), AppView(root, self)

    def start_task(self):
        self.model.run_task(self.on_progress)

    def on_progress(self, progress):
        self.view.update_progress(progress)
