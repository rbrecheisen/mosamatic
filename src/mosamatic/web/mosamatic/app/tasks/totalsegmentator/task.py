import os
import logging

from .. import TaskJob, TaskForm

logger = logging.getLogger(__name__)

class TotalSegmentatorTaskForm(TaskForm):
    pass


class TotalSegmentatorTaskJob(TaskJob):

    def get_form(self):
        return TotalSegmentatorTaskForm(self.task)

    def execute(self):
        print('')
        self.task_job_begin()
        input_dataset = self.get_input_dataset(self.task.parameters['input'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])
        fast = self.get_bool(self.task.parameters['fast'])
        if fast:
            fast = '--fast'
        statistics = self.get_bool(self.task.parameters['statistics'])
        if statistics:
            statistics = '--statistics'
        radiomics = self.get_bool(self.task.parameters['radiomics'])
        if radiomics:
            radiomics = '--radiomics'
        files = self.get_files(input_dataset)
        cmd = f'TotalSegmentator {statistics} {radiomics} {fast} -i {files[0].path} -o {output_dataset.data_dir}'
        logger.info(f'Running command: {cmd}')
        os.system(cmd)
        for f in os.listdir(output_dataset.data_dir):
            f_path = os.path.join(output_dataset.data_dir, f)
            self.create_output_file(f_path, output_dataset)
            logger.info(f'Added {f_path}')
        self.task_job_end()
