'''Importing routes to the administration panel'''
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('', include('exam.urls')),
    path('admin-django/', admin.site.urls),
]
