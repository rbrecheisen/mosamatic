import os
import json
import uuid

from django import forms
from django.conf import settings
from django.db.models import Q

from ..models import DataSetModel, FilePathModel


class TaskErrors(Exception):

    def __init__(self, messages=None):
        self.messages = [] if messages is None else messages

    def add_message(self, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def occurred(self):
        return len(self.messages) > 0


class TaskJob:

    def __init__(self, task):
        self.task = task
        self.task_type = self.task.task_type
        self.errors = TaskErrors()

    @staticmethod
    def get_files(dataset):
        return FilePathModel.objects.filter(dataset=dataset).all()

    @staticmethod
    def get_input_dataset(name):
        return DataSetModel.objects.get(pk=name)

    def get(self, name):
        if name not in self.task.parameters.keys():
            return None
        return self.task.parameters[name]

    def get_str(self, name):
        return self.get(name)

    def get_int(self, name, default=0):
        value = self.get(name)
        if value == '' or value is None:
            return default
        return int(self.get(name))

    def get_float(self, name, default=0.0):
        value = self.get(name)
        if value == '' or value is None:
            return default
        return float(self.get(name))

    def get_bool(self, name, default=False):
        value = self.get(name)
        if value == '' or value == 'false' or value == '0' or value is None:
            return False
        if value == 'true' or value == '1' or value == 'on':
            return True
        return default

    def get_list(self, name, of=str, sep=','):
        if name not in self.task.parameters.keys():
            return []
        my_list = []
        for item in self.task.parameters[name].split(sep):
            my_list.append(of(item).strip())
        return my_list

    def get_dataset(self, name):
        if name in self.task.parameters.keys():
            return DataSetModel.objects.filter(name=name).first()
        return None

    def create_output_dataset(self, name=''):
        data_dir = os.path.join(settings.MEDIA_ROOT, str(uuid.uuid4()))
        os.makedirs(data_dir, exist_ok=False)
        base_name = f'output-{self.task.task_type.name.lower()}'
        if name != '':
            base_name = name
        else:
            name = base_name
        index = 1
        dataset = DataSetModel.objects.filter(name=name).first()
        while dataset is not None:
            if index > 10:
                raise RuntimeError('Maximum nr. tries creating output dataset!')
            name = f'{base_name}-{index}'
            dataset = DataSetModel.objects.filter(name=name).first()
            index += 1
        return DataSetModel.objects.create(name=name, data_dir=data_dir, owner=self.task.owner)

    @staticmethod
    def create_output_file(file_name, dataset):
        file_path = os.path.join(dataset.data_dir, file_name)
        return FilePathModel.objects.create(name=file_name, path=file_path, dataset=dataset)

    def create_errors_dataset(self, dataset=None):
        if dataset is None:
            dataset = self.create_output_dataset('errors')
        errors_file = os.path.join(dataset.data_dir, 'errors.txt')
        errors = json.dumps(self.errors.get_messages(), indent=4)
        with open(errors_file, 'w') as f:
            f.write(errors)
        self.create_output_file('errors.txt', dataset)

    def execute(self):
        raise TaskErrors(messages=['Method execute() not implemented'])

    def task_job_begin(self):
        pass

    def task_job_end(self):
        if self.errors.occurred():
            raise self.errors


class TaskJobManager:

    @staticmethod
    def load_task_job(task):
        import importlib
        items = task.task_type.class_path.split('.')
        module_name = '.'.join(items[:-1])
        class_name = items[-1]
        module = importlib.import_module(module_name)
        return getattr(module, class_name)(task)

    def execute(self, task):
        task_job = self.load_task_job(task)
        task_job.execute()
        task.job_status = 'finished'
        task.job_id = None
        task.save()


class TaskForm(forms.Form):

    def __init__(self, task):
        super(TaskForm, self).__init__()
        self.task = task
        self.generate_fields(self.task.task_type)

    def generate_fields(self, task_type):
        parameters = task_type.parameters
        for parameter in parameters:
            if parameter['data_type'] == 'int':
                self.add_int_field(parameter)
            elif parameter['data_type'] == 'float':
                self.add_float_field(parameter)
            elif parameter['data_type'] == 'bool':
                self.add_bool_field(parameter)
            elif parameter['data_type'] == 'str':
                self.add_char_field(parameter)
            elif parameter['data_type'] == 'list':
                self.add_list_field(parameter)
            elif parameter['data_type'] == 'dataset':
                self.add_dataset_selector(parameter)
            else:
                raise RuntimeError('Illegal parameter data type {}'.format(parameter['data_type']))

    def add_int_field(self, parameter):
        if 'name' not in parameter.keys():
            raise RuntimeError(f'Parameter does not contain "name"')
        name = parameter['name']
        if 'display_name' not in parameter.keys():
            raise RuntimeError(f'Parameter {name} does not contain "display_name"')
        display_label = parameter['display_name']
        if 'required' in parameter.keys():
            required = parameter['required']
        else:
            required = False
        if 'min_value' in parameter.keys():
            min_value = int(parameter['min_value'])
        else:
            min_value = -99999999
        if 'max_value' in parameter.keys():
            max_value = int(parameter['max_value'])
        else:
            max_value = 99999999
        if 'default_value' in parameter.keys():
            default_value = parameter['default_value']
        else:
            default_value = None
        self.fields[name] = forms.IntegerField(
            label=display_label,
            required=required,
            min_value=min_value,
            max_value=max_value,
            initial=default_value,
        )

    def add_float_field(self, parameter):
        if 'name' not in parameter.keys():
            raise RuntimeError(f'Parameter does not contain "name"')
        name = parameter['name']
        if 'display_name' not in parameter.keys():
            raise RuntimeError(f'Parameter {name} does not contain "display_name"')
        display_label = parameter['display_name']
        if 'required' in parameter.keys():
            required = parameter['required']
        else:
            required = False
        if 'min_value' in parameter.keys():
            min_value = float(parameter['min_value'])
        else:
            min_value = -99999999
        if 'max_value' in parameter.keys():
            max_value = float(parameter['max_value'])
        else:
            max_value = 99999999
        if 'default_value' in parameter.keys():
            default_value = parameter['default_value']
        else:
            default_value = None
        self.fields[name] = forms.FloatField(
            label=display_label,
            required=required,
            min_value=min_value,
            max_value=max_value,
            initial=default_value,
        )

    def add_bool_field(self, parameter):
        if 'name' not in parameter.keys():
            raise RuntimeError(f'Parameter does not contain "name"')
        name = parameter['name']
        if 'display_name' not in parameter.keys():
            raise RuntimeError(f'Parameter {name} does not contain "display_name"')
        display_label = parameter['display_name']
        if 'required' in parameter.keys():
            required = parameter['required']
        else:
            required = False
        if 'default_value' in parameter.keys():
            default_value = parameter['default_value']
        else:
            default_value = None
        self.fields[name] = forms.BooleanField(
            label=display_label,
            required=required,
            initial=default_value,
        )

    def add_char_field(self, parameter):
        if 'name' not in parameter.keys():
            raise RuntimeError(f'Parameter does not contain "name"')
        name = parameter['name']
        if 'display_name' not in parameter.keys():
            raise RuntimeError(f'Parameter {name} does not contain "display_name"')
        display_label = parameter['display_name']
        if 'required' in parameter.keys():
            required = parameter['required']
        else:
            required = False
        if 'min_length' in parameter.keys():
            min_length = int(parameter['min_length'])
        else:
            min_length = 0
        if 'max_length' in parameter.keys():
            max_length = int(parameter['max_length'])
        else:
            max_length = 9999
        if 'default_value' in parameter.keys():
            default_value = parameter['default_value']
        else:
            default_value = None
        self.fields[name] = forms.CharField(
            label=display_label,
            required=required,
            min_length=min_length,
            max_length=max_length,
            initial=default_value,
        )

    def add_list_field(self, parameter):
        if 'name' not in parameter.keys():
            raise RuntimeError('Parameter does not contain "name"')
        name = parameter['name']
        if 'display_name' not in parameter.keys():
            raise RuntimeError(f'Parameter {name} does not contain "display_name"')
        display_label = parameter['display_name']
        if 'required' in parameter.keys():
            required = parameter['required']
        else:
            required = True
        if 'default_value' in parameter.keys():
            default_value = parameter['default_value']
        else:
            default_value = None
        self.fields[name] = forms.CharField(
            label=display_label,
            required=required,
            min_length=0,
            max_length=9999,
            initial=default_value,
        )

    def add_dataset_selector(self, parameter):
        if 'name' not in parameter.keys():
            raise RuntimeError(f'Parameter does not contain "name"')
        name = parameter['name']
        if 'display_name' not in parameter.keys():
            raise RuntimeError(f'Parameter {name} does not contain "display_name"')
        display_label = parameter['display_name']
        if 'required' in parameter.keys():
            required = parameter['required']
        else:
            required = True
        self.fields[name] = forms.ChoiceField(
            label=display_label,
            required=required,
            choices=self.get_dataset_names(),
        )

    def get_datasets(self):
        return DataSetModel.objects.filter(Q(owner=self.task.owner) | Q(public=True))

    def get_dataset_names(self):
        datasets = self.get_datasets()
        names = []
        for dataset in datasets:
            names.append((dataset.id, dataset.name))
        return names
