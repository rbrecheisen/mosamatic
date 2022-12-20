import os
import shutil
import logging
import pydicom

from barbell2.imaging.utils import is_dicom_file
from .. import TaskJob, TaskForm

logger = logging.getLogger(__name__)


class DicomToRawTaskForm(TaskForm):
    pass


class DicomToRawTaskJob(TaskJob):

    def get_form(self):
        return DicomToRawTaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        input_dataset = self.get_input_dataset(self.task.parameters['input'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])
        file_path_models = self.get_files(input_dataset)
        for file_path_model in file_path_models:
            file_path = file_path_model.path
            if is_dicom_file(file_path):
                output_dicom_file_name = os.path.split(file_path)[1]
                output_dicom_file_path = os.path.join(output_dataset.data_dir, output_dicom_file_name)
                p = pydicom.dcmread(file_path)
                if p.file_meta.TransferSyntaxUID.is_compressed:
                    logger.info(f'Decompressing {output_dicom_file_path}...')
                    p.decompress()
                p.save_as(output_dicom_file_path)
                self.create_output_file(output_dicom_file_name, output_dataset)
            else:
                shutil.copy(file_path, output_dataset.data_dir)
                self.create_output_file(os.path.split(file_path)[1], output_dataset)
        self.task_job_end()
