import os
import json
import shutil
import pydicom
import pydicom.errors
import logging

from .. import TaskJob, TaskForm


logger = logging.getLogger(__name__)


class CheckDicomsTaskForm(TaskForm):
    pass


class CheckDicomsTaskJob(TaskJob):

    def get_form(self):
        return CheckDicomsTaskForm(self.task)

    def execute(self):

        self.task_job_begin()

        input_dataset = self.get_input_dataset(self.get_str('input'))
        output_dataset = self.create_output_dataset(name=self.get_str('output_dataset_name'))
        file_path_models = self.get_files(input_dataset)

        extensions_to_ignore = self.get_list('extensions_to_ignore')
        logger.error(f'extensions_to_ignore: {extensions_to_ignore}')

        add_ignored_files_to_output = self.get_bool('add_ignored_files_to_output')
        logger.error(f'add_ignored_files_to_output: {add_ignored_files_to_output}')

        correct_dicoms = []

        for file_path_model in file_path_models:

            dcm_file_path = file_path_model.path
            messages = []

            # Check if we can ignore this file based on extension
            extension = os.path.splitext(dcm_file_path)[1][1:]
            if extension in extensions_to_ignore:
                # Check if we should the ignored file to the output dataset
                if add_ignored_files_to_output:
                    shutil.copy(dcm_file_path, output_dataset.data_dir)
                    self.create_output_file(os.path.split(dcm_file_path)[1], output_dataset)
                continue

            # Check DICOM properties
            try:
                p = pydicom.dcmread(dcm_file_path)
                if p.file_meta.TransferSyntaxUID.is_compressed:
                    messages.append(f'{dcm_file_path}: Pixel data is compressed')
                required_attributes = self.get_list('required_attributes')
                for attribute in required_attributes:
                    if attribute not in p:
                        messages.append(f'{dcm_file_path}: Attribute {attribute} missing')
                if 'Rows' in p and 'Columns' in p:
                    x = ''
                    if p.Rows != self.get_int('rows'):
                        x += 'Nr. rows should be {}, but has size ({}x{}) '.format(self.get_int('rows'), p.Rows, p.Columns)
                    if p.Columns != self.get_int('columns'):
                        x += 'Nr. columns should be {}, but has size ({}x{})'.format(self.get_int('columns'), p.Rows, p.Columns)
                    if x != '':
                        messages.append('{}: {}'.format(dcm_file_path, x))
            except pydicom.errors.InvalidDicomError as e:
                messages.append('{}: {}'.format(dcm_file_path, e))
            except ValueError as e:
                # May be raised when there's something wrong with the pixel data
                messages.append('{}: {}'.format(dcm_file_path, e))

            # If there were errors, then pass them to the task error list
            if len(messages) > 0:
                for message in messages:
                    self.errors.add_message(message)
            # If not, add DICOM to list of correct DICOM files
            else:
                correct_dicoms.append(dcm_file_path)

        # Add correct DICOMs to output dataset
        for dicom_file in correct_dicoms:
            shutil.copy(dicom_file, output_dataset.data_dir)
            self.create_output_file(os.path.split(dicom_file)[1], output_dataset)

        # Check for errors. If there were any, report them in the task list and add error file
        # to the output dataset
        if self.errors.occurred():
            errors_dataset = self.create_output_dataset(output_dataset.name + '_errors')
            self.create_errors_dataset(dataset=errors_dataset)

        self.task_job_end()
