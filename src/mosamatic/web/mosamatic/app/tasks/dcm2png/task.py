import os

from .. import TaskJob, TaskForm
from barbell2.imaging import dcm2npy, npy2png
from barbell2.imaging.utils import is_dicom_file


class DicomToPngTaskForm(TaskForm):
    pass


class DicomToPngTaskJob(TaskJob):

    def get_form(self):
        return DicomToPngTaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        input_dataset = self.get_input_dataset(self.task.parameters['input'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])
        file_path_models = self.get_files(input_dataset)
        for file_path_model in file_path_models:
            dcm_file_path = file_path_model.path
            if is_dicom_file(dcm_file_path):
                d2n = dcm2npy.Dicom2Numpy(dcm_file_path)
                d2n.set_normalize_enabled(self.get_bool('normalize_enabled'))
                window_width = self.get_int('window_width', None)
                window_level = self.get_int('window_level', None)
                if window_width is not None and window_level is not None:
                    d2n.set_window([self.get_int('window_width'), self.get_int('window_level')])
                n2p = npy2png.Numpy2Png(d2n.execute())
                n2p.set_output_dir(output_dataset.data_dir)
                color_map = self.get_str('color_map')
                if color_map != '':
                    n2p.set_color_map(color_map)
                n2p.execute()
                png_file_path = os.path.split(dcm_file_path)[1] + '.png'
                os.rename(n2p.png_file_path, png_file_path)
                self.create_output_file(png_file_path, output_dataset)
        self.task_job_end()
