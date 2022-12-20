import os
import shutil

from barbell2.imaging import tag2dcm
from barbell2.imaging.utils import get_tag_file_for_dicom, is_dicom_file
from .. import TaskJob, TaskForm


class TagToDicomTaskForm(TaskForm):
    pass


class TagToDicomTaskJob(TaskJob):

    def get_form(self):
        return TagToDicomTaskForm(self.task)

    @staticmethod
    def convert_tag_to_dicom(dcm_file, output_dir):
        t2d = tag2dcm.Tag2Dicom(get_tag_file_for_dicom(dcm_file), dcm_file)
        t2d.set_output_dir(output_dir)
        t2d.execute()
        return t2d

    def execute(self):
        self.task_job_begin()
        input_dataset = self.get_input_dataset(self.task.parameters['input'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])
        file_path_models = self.get_files(input_dataset)
        for file_path_model in file_path_models:
            dcm_file_path = file_path_model.path
            if is_dicom_file(dcm_file_path):
                t2d = self.convert_tag_to_dicom(dcm_file_path, output_dataset.data_dir)
                self.create_output_file(
                    t2d.tag_dcm_file_name, output_dataset)
                shutil.copy(dcm_file_path, output_dataset.data_dir)
                self.create_output_file(os.path.split(dcm_file_path)[1], output_dataset)
        self.task_job_end()
