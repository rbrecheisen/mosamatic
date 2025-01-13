import os
import threading


class DecompressDicomTask:
    def __init__(self, root):
        self.root = root

    def run(self, file_dir, callback):
        def task():
            files = os.listdir(file_dir)
            nr_steps = len(files)
            for step in range(nr_steps):
                print(os.path.join(file_dir, files[step]))
                progress = int(((step + 1) / (nr_steps)) * 100)
                self.root.after(0, callback, progress)
        thread = threading.Thread(target=task, daemon=True)
        thread.start()