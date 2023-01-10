import os
import uuid
import shutil
import redis
import django_rq

from rq.command import send_stop_job_command
from rq.registry import StartedJobRegistry
from rq.exceptions import NoSuchJobError
from django.shortcuts import render
from django_rq.jobs import Job
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.conf import settings
from django.db.models import Q
from os.path import basename
from zipfile import ZipFile
from barbell2.imaging import dcm2npy, npy2png

from .models import DataSetModel, FilePathModel, TaskModel, TaskTypeModel
from .tasks import TaskJobManager, TaskErrors


def is_auto_refresh(request):
    return True if request.GET.get('auto-refresh', '0') == '1' else False


def render_datasets_page(request):
    return render(request, 'datasets.html', context={
        'datasets': get_datasets(request.user)
    })


def render_dataset_page(request, dataset):
    return render(request, 'dataset.html', context={
        'dataset': dataset,
        'files': get_file_paths(dataset),
    })


def render_tasks_page(request):
    return render(request, 'tasks.html', context={
        'task_types': get_task_types(),
        'tasks': get_tasks(request.user),
        'auto_refresh': is_auto_refresh(request),
    })


def render_task_page(request, task):
    return render(request, 'task.html', context={
        'task': task,
        'task_form': get_task_form(task),
    })


def render_viewer(request, dataset):
    return render(request, 'viewer.html', context={
        'dataset': dataset,
        'files': get_file_paths(dataset),
    })


def process_uploaded_files(request):
    file_paths = []
    file_names = []
    files = request.POST.getlist('files.path')
    if files is None or len(files) == 0:
        files = request.FILES.getlist('files')
        if files is None or len(files) == 0:
            raise RuntimeError('File upload without files in either POST or FILES object')
        else:
            for f in files:
                if isinstance(f, TemporaryUploadedFile):
                    file_paths.append(f.temporary_file_path())
                    file_names.append(f.name)
                elif isinstance(f, InMemoryUploadedFile):
                    file_path = default_storage.save('{}'.format(uuid.uuid4()), ContentFile(f.read()))
                    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    file_paths.append(file_path)
                    file_names.append(f.name)
                elif isinstance(f, str):
                    file_paths.append(f)
                    file_names.append(os.path.split(f)[1])
                else:
                    raise RuntimeError('Unknown file type {}'.format(type(f)))
    else:
        file_paths = files
        file_names = request.POST.getlist('files.name')
    return file_paths, file_names


def get_datasets(user):
    if not user.is_staff:
        return DataSetModel.objects.filter(Q(owner=user) | Q(public=True))
    return DataSetModel.objects.all()


def get_dataset(dataset_id, user):
    return DataSetModel.objects.get(pk=dataset_id)


def create_dataset(user, name=None):
    if name:
        ds_name = name
    else:
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S.%f')
        ds_name = 'dataset-{}'.format(timestamp)
    dataset = DataSetModel.objects.create(name=ds_name, owner=user)
    return dataset


def create_file_path(path, dataset):
    return FilePathModel.objects.create(
        name=os.path.split(path)[1], path=path, dataset=dataset)


def create_dataset_from_files(file_paths, file_names, user):
    if len(file_paths) == 0 or len(file_names) == 0:
        return None
    dataset = create_dataset(user)
    for i in range(len(file_paths)):
        source_path = file_paths[i]
        target_name = file_names[i]
        target_path = os.path.join(dataset.data_dir, target_name)
        shutil.move(source_path, target_path)
        create_file_path(path=target_path, dataset=dataset)
    return dataset


def rename_dataset(dataset, new_name):
    dataset.name = new_name
    dataset.save()
    return dataset


def make_dataset_public(dataset, public=True):
    dataset.public = public
    dataset.save()
    return dataset


def delete_dataset(dataset):
    dataset.delete()


def get_file_paths(dataset):
    return FilePathModel.objects.filter(dataset=dataset).all()


def get_zip_file_from_dataset(dataset):
    file_path_models = get_file_paths(dataset)
    zip_file_path = os.path.join(dataset.data_dir, '{}.zip'.format(dataset.name))
    with ZipFile(zip_file_path, 'w') as zip_obj:
        for file_path_model in file_path_models:
            zip_obj.write(file_path_model.path, arcname=basename(file_path_model.path))
    return zip_file_path


def get_task_types():
    return TaskTypeModel.objects.order_by('display_name')


def get_task_type(task_type_id):
    return TaskTypeModel.objects.get(pk=task_type_id)


def create_task(task_type_id, user):
    t = TaskModel.objects.create(
        task_type=get_task_type(task_type_id),
        owner=user,
    )
    return t


def update_task_status(task):
    try:
        connection = redis.Redis(host=settings.RQ_QUEUES['default']['HOST'])
        job = Job.fetch(
            task.job_id, connection=connection)
        task.job_status = job.get_status()
        task.save()
    except NoSuchJobError:
        pass
    return task


def get_tasks(user):
    tasks = TaskModel.objects.filter(owner=user).order_by('-created').all()
    for task in tasks:
        update_task_status(task)
    return tasks


def get_task(task_id):
    task = TaskModel.objects.get(pk=task_id)
    update_task_status(task)
    return task


def get_task_form(task):
    manager = TaskJobManager()
    task_job = manager.load_task_job(task)
    return task_job.get_form()


def start_task(task):
    q = django_rq.get_queue('default')
    job = q.enqueue(start_task_job, task)
    task.job_id = job.id
    task.job_status = job.get_status()
    task.save()
    return task


def cancel_task(task):
    try:
        connection = redis.Redis(host=settings.RQ_QUEUES['default']['HOST'])
        job = Job.fetch(task.job_id, connection=connection)
        if job.is_started:
            send_stop_job_command(
                connection=connection, job_id=task.job_id)
    except NoSuchJobError:
        pass
    task.job_status = 'cancelled'
    task.save()
    return task


def cancel_all_tasks_and_orphan_jobs(queue='default'):
    connection = redis.Redis(host=settings.RQ_QUEUES['default']['HOST'])
    registry = StartedJobRegistry(queue, connection=connection)
    for job_id in registry.get_job_ids():
        task = TaskModel.objects.filter(job_id=job_id).first()
        if task:
            cancel_task(task)
        else:
            send_stop_job_command(connection=connection, job_id=job_id)


def fail_task(task, errors):
    task = cancel_task(task)
    task.job_status = 'failed'
    task.errors = errors
    task.save()
    return task


def delete_task(task):
    task = cancel_task(task)
    task.delete()


def clear_queue():
    q = django_rq.get_queue('default')
    q.delete()


@django_rq.job
def start_task_job(task):
    manager = TaskJobManager()
    try:
        manager.execute(task)
    except TaskErrors as e:
        fail_task(task, e.messages)
