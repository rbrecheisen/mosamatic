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
        files = self.get_files(input_dataset)
        if len(files) > 1:
            raise Exception(f'Only one NIFTI file supported! Found {len(files)}')
        for f in files:
            cmd = f'TotalSegmentator -i {f.path} -o {output_dataset.data_dir}'
            print(f'Running command {cmd}')
            subprocess.check_output(cmd)
            for f_seg in os.listdir(output_dataset.data_dir):
                f_seg_path = os.path.join(output_dataset.data_dir, f_seg)
                self.create_output_file(f_seg_path, output_dataset)
                print(f'Added {f_seg_path}')
            break
        self.task_job_end()
