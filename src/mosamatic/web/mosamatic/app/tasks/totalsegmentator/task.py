import os
import subprocess

from .. import TaskJob, TaskForm


class TotalSegmentatorTaskForm(TaskForm):
    pass


class TotalSegmentatorTaskJob(TaskJob):

    def get_form(self):
        return TotalSegmentatorTaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        input_dataset = self.get_input_dataset(self.task.parameters['input'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])
        result = subprocess.check_output('TotalSegmentator')
        if result != 0:
            raise Exception('TotalSegmentator tool not installed!')
        files = self.get_files(input_dataset)
        if len(files) > 1:
            raise Exception(f'Only one NIFTI file supported! Found {len(files)}')
        for f in files:
            print(f'Processing {f.path} and segmenting structures...')
            os.system(f'TotalSegmentator -i {f.path} -o {output_dataset.data_dir}')
            file_name = os.path.split(f.path)[1]
            self.create_output_file(os.path.join(output_dataset.data_dir, file_name), output_dataset)
        self.task_job_end()
