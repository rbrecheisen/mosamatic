from mosamatic.view import View
from mosamatic.processing.decompress_dicom import DecompressDicomTask


class Controller:
    def __init__(self, root):
        self.view = View(root, self)
        self.tasks = {
            'decompress_dicom': DecompressDicomTask(root),
        }

    def decompress_dicom(self, file_dir):
        self.tasks['decompress_dicom'].run(file_dir, self.on_progress)

    def on_progress(self, progress):
        self.view.update_progress(progress)
