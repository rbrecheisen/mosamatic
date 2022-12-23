import os
import logging

from .. import TaskJob, TaskForm
from barbell2.imaging import dcm2nifti
from barbell2.imaging.utils import is_dicom_file

logger = logging.getLogger(__name__)


class DicomToNiftiTaskForm(TaskForm):
    pass


class DicomToNiftiTaskJob(TaskJob):

    def get_form(self):
        return DicomToNiftiTaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        input_dataset = self.get_input_dataset(self.task.parameters['input'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])
        output_file_path = os.path.join(output_dataset.data_dir, output_dataset.name + '.nii.gz')
        d2n = dcm2nifti.Dicom2NiftiWithHeaderInfo(input_dataset.data_dir, output_file_path)
        d2n.execute()
        self.create_output_file(output_file_path, output_dataset)
        self.task_job_end()
