import time
import threading


class AppModel:
    def __init__(self, root):
        self.root = root

    def run_task(self, callback):
        def task():
            for i in range(1, 6):
                time.sleep(1)  # Simulate work
                self.root.after(0, callback, i * 20)  # Schedule progress updates in the main thread
        thread = threading.Thread(target=task, daemon=True)
        thread.start()