import os
import shutil

from .. import TaskJob, TaskForm
from barbell2.imaging import selectl3

logger = logging.getLogger(__name__)


class SelectL3TaskForm(TaskForm):
    pass


class SelectL3TaskJob(TaskJob):

    def get_form(self):
        return SelectL3TaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        dicom_series_dataset = self.get_input_dataset(self.task.get_param('dicom_series'))
        nifti_image_dataset = self.get_input_dataset(self.task.get_param('nifti_image'))
        nifti_image = self.get_files(nifti_image_dataset)[0]
        nifti_roi_dataset = self.get_input_dataset(self.task.get_param('nifti_roi'))
        nifti_roi = self.get_files(nifti_roi_dataset)[0]
        alpha = self.get_float('alpha')
        output_dataset = self.create_output_dataset(name=self.task.get_param('output_dataset_name'))
        selector = selectl3.L3Selector(
            dicom_series_dataset.data_dir,
            nifti_image.path,
            nifti_roi.path,
            alpha,
        )
        l3_path = selector.execute()
        logger.info(f'L3 found: {l3_path}')
        shutil.copy(l3_path, output_dataset.data_dir)
        l3_name = os.path.split(l3_path)[1]
        self.create_output_file(l3_name, output_dataset)
        self.task_job_end()
