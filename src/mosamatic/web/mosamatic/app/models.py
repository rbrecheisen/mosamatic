import os
import uuid
import shutil

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver

ID_LENGTH = 64


class DataSetModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=1024, editable=True, null=False, unique=True)
    data_dir = models.CharField(max_length=2048, editable=False, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, editable=False, related_name='+', on_delete=models.CASCADE)
    public = models.BooleanField(default=False, editable=True)

    def __str__(self):
        return self.name


class FilePathModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=256, editable=False, null=False)
    path = models.CharField(max_length=2048, editable=False, null=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    dataset = models.ForeignKey(DataSetModel, on_delete=models.CASCADE)

    def __str__(self):
        return os.path.split(str(self.path))[1]


class TaskTypeModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=1024, editable=False, null=False, unique=True)
    display_name = models.CharField(max_length=2048, null=False)
    parameters = models.JSONField(null=True)
    class_path = models.CharField(max_length=1024, null=False)

    def __str__(self):
        return f'TaskTypeModel object ({self.name})'


class TaskModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    task_type = models.ForeignKey(TaskTypeModel, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(null=True)
    inputs = ArrayField(models.UUIDField(), null=True)
    job_id = models.CharField(max_length=128, null=True)
    job_status = models.CharField(max_length=16, null=False, default='idle')
    errors = ArrayField(models.CharField(max_length=1024, null=True), null=True)
    owner = models.ForeignKey(
        User, editable=False, related_name='+', on_delete=models.CASCADE)

    def get_param(self, name):
        if name in self.parameters.keys():
            return self.parameters[name]
        else:
            return None


@receiver(models.signals.post_save, sender=DataSetModel)
def dataset_post_save(sender, instance, **kwargs):
    if not instance.data_dir:
        instance.data_dir = os.path.join(settings.MEDIA_ROOT, str(instance.id))
        os.makedirs(instance.data_dir, exist_ok=False)
        instance.save()


@receiver(models.signals.post_delete, sender=DataSetModel)
def dataset_post_delete(sender, instance, **kwargs):
    if os.path.isdir(instance.data_dir):
        shutil.rmtree(instance.data_dir)
