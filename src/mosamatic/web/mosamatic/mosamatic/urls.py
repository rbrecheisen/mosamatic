from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('app.urls')),
    path('admin/', admin.site.urls),
    path('django-rq', include('django_rq.urls')),
    path('session_security', include('session_security.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
