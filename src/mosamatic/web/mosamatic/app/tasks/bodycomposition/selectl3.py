from .. import TaskJob, TaskForm
from barbell2.imaging import selectl3


class SelectL3TaskForm(TaskForm):
    pass


class SelectL3TaskJob(TaskJob):

    def get_form(self):
        return SelectL3TaskForm(self.task)

    def execute(self):
        self.task_job_begin()
        dicom_series_dataset = self.get_input_dataset(self.task.get_param('dicom_series'))
        nifti_image_dataset = self.get_input_dataset(self.task.get_param('nifti_image'))
        nifti_roi_dataset = self.get_input_dataset(self.task.get_param('nifti_roi'))
        output_dataset = self.create_output_dataset(name=self.task.get_param('output_dataset_name'))
        selector = selectl3.L3Selector(

        )
        selector.execute()
        self.task_job_end()
