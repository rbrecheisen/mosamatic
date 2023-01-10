import os
import shutil
import logging

from .. import TaskJob, TaskForm
from barbell2.imaging import selectl3

logger = logging.getLogger(__name__)


class SelectL3AllTaskForm(TaskForm):
    pass


class SelectL3AllTaskJob(TaskJob):

    def get_form(self):
        return SelectL3AllTaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        alpha = 0.5
        dicom_series_dataset = self.get_input_dataset(self.task.get_param('dicom_series'))
        output_dataset = self.create_output_dataset(name=self.task.get_param('output_dataset_name'))
        # selector = selectl3.L3Selector(
        #     dicom_series_dataset.data_dir,
        #     nifti_image.path,
        #     nifti_roi.path,
        #     alpha,
        # )
        # l3_path = selector.execute()
        # logger.info(f'L3 found: {l3_path}')
        # shutil.copy(l3_path, output_dataset.data_dir)
        # l3_name = os.path.split(l3_path)[1]
        # self.create_output_file(l3_name, output_dataset)
        self.task_job_end()
