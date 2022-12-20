from django.contrib import admin

from .models import DataSetModel, FilePathModel, TaskTypeModel, TaskModel


@admin.register(DataSetModel)
class DataSetModelAdmin(admin.ModelAdmin):
    list = (
        'name',
        'created',
        'owner',
    )


@admin.register(FilePathModel)
class FilePathModelAdmin(admin.ModelAdmin):
    list = (
        'name',
        'path',
        'created',
        'dataset',
    )


@admin.register(TaskTypeModel)
class TaskTypeModelAdmin(admin.ModelAdmin):
    list = (
        'name',
        'display_name'
        'parameters',
        'class_path',
    )


@admin.register(TaskModel)
class TaskModelAdmin(admin.ModelAdmin):
    list = (
        'task_type',
        'created',
        'started',
        'stopped',
        'parameters',
        'inputs',
        'job_id',
        'job_status',
    )
