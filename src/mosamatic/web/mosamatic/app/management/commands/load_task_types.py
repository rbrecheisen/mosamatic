from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import TaskTypeModel


class Command(BaseCommand):

    help = 'Loads task types'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            for item in settings.TASK_TYPES:
                name = item['name']
                task_type = TaskTypeModel.objects.filter(name=name).first()
                if task_type is None:
                    TaskTypeModel.objects.create(
                        name=name,
                        display_name=item['display_name'],
                        class_path=item['class_path'],
                        parameters=item['parameters'],
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully created task type {name}'))
                else:
                    task_type.display_name = item['display_name']
                    task_type.class_path = item['class_path']
                    task_type.parameters = item['parameters']
                    task_type.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated task type {name}'))
            # for name, data in settings.TASK_TYPES.items():
            #     task_type = TaskTypeModel.objects.filter(name=name).first()
            #     if task_type is None:
            #         TaskTypeModel.objects.create(
            #             name=name,
            #             display_name=data['display_name'],
            #             class_path=data['class_path'],
            #             parameters=data['parameters'],
            #         )
            #         self.stdout.write(self.style.SUCCESS(f'Successfully created task type {name}'))
            #     else:
            #         task_type.display_name = data['display_name']
            #         task_type.class_path = data['class_path']
            #         task_type.parameters = data['parameters']
            #         task_type.save()
            #         self.stdout.write(self.style.SUCCESS(f'Successfully updated task type {name}'))
        except KeyError:
            raise CommandError('TASK_TYPES not in Django settings')
