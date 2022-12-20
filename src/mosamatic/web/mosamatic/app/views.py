from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from wsgiref.util import FileWrapper

from . import backend


@login_required
def auth(_):
    return HttpResponse(status=200)


@login_required
def datasets(request):
    if request.method == 'POST':
        file_paths, file_names = backend.process_uploaded_files(request)
        backend.create_dataset_from_files(file_paths, file_names, request.user)
    return backend.render_datasets_page(request)


@login_required
def dataset(request, dataset_id):
    if request.method == 'GET':
        ds = backend.get_dataset(dataset_id, request.user)
        action = request.GET.get('action', None)
        if action == 'download':
            zip_file_path = backend.get_zip_file_from_dataset(ds)
            with open(zip_file_path, 'rb') as f:
                response = HttpResponse(FileWrapper(f), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(ds.name)
            return response
        elif action == 'delete':
            backend.delete_dataset(ds)
            return backend.render_datasets_page(request)
        elif action == 'rename':
            ds = backend.rename_dataset(ds, request.GET.get('new_name'))
        elif action == 'make-public':
            ds = backend.make_dataset_public(ds)
        elif action == 'make-private':
            ds = backend.make_dataset_public(ds, public=False)
        else:
            pass
        return backend.render_dataset_page(request, ds)
    else:
        pass
    return HttpResponseForbidden('Wrong method')


@login_required
def tasks(request):
    if request.method == 'GET':
        action = request.GET.get('action', None)
        if action is not None:
            if action == 'cancel':
                backend.cancel_all_tasks_and_orphan_jobs()
            else:
                pass
            return redirect('/tasks/')
        else:
            pass
        return backend.render(request, 'tasks.html', context={
            'task_types': backend.get_task_types(),
            'tasks': backend.get_tasks(request.user),
            'auto_refresh': backend.is_auto_refresh(request),
    })

    elif request.method == 'POST':
        t = backend.create_task(request.POST.get('task_type_id'), request.user)
        return backend.render_task_page(request, t)
    else:
        pass
    return HttpResponseForbidden('Wrong method')


@login_required
def task(request, task_id):
    if request.method == 'GET':
        t = backend.get_task(task_id)
        action = request.GET.get('action', None)
        if action is not None:
            if action == 'cancel':
                backend.cancel_task(t)
            elif action == 'delete':
                backend.delete_task(t)
            else:
                pass
            return redirect('/tasks/')
        else:
            pass
        return backend.render_task_page(request, t)
    elif request.method == 'POST':
        t = backend.get_task(task_id)
        t.parameters = dict(request.POST.items())
        backend.start_task(t)
        return redirect('/tasks/')
    else:
        pass
    return HttpResponseForbidden('Wrong method')
