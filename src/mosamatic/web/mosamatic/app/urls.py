from django.urls import path
from . import views


urlpatterns = [

    path('', views.datasets),
    path('auth', views.auth),
    path('datasets/', views.datasets),
    path('datasets/<str:dataset_id>', views.dataset),
    path('tasks/', views.tasks),
    path('tasks/<str:task_id>', views.task),
]
