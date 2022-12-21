import os
import logging

from .. import TaskJob, TaskForm
from barbell2.imaging import totalseg

logger = logging.getLogger(__name__)

class TotalSegmentatorTaskForm(TaskForm):
    pass


class TotalSegmentatorTaskJob(TaskJob):

    def get_form(self):
        return TotalSegmentatorTaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        input_dataset = self.get_input_dataset(self.task.get_param('input'))
        output_dataset = self.create_output_dataset(name=self.task.get_param('output_dataset_name'))
        fast = self.get_bool('fast')
        statistics = self.get_bool('statistics')
        radiomics = self.get_bool('radiomics')
        files = self.get_files(input_dataset)
        nifti_path = files[0].path
        output_dir = output_dataset.data_dir
        totalseg = totalseg.TotalSegmentator(nifti_path, output_dir)
        totalseg.fast = fast
        totalseg.statistics = statistics
        totalseg.radiomics = radiomics
        totalseg.execute()
        for f in os.listdir(output_dataset.data_dir):
            f_path = os.path.join(output_dataset.data_dir, f)
            self.create_output_file(f_path, output_dataset)
            logger.info(f'Added {f_path}')
        self.task_job_end()
