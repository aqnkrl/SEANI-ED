'''Importing routes to the administration panel'''
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', include('home.urls')),
    path('', include('exam.urls')),
    path('admin-django/', admin.site.urls),
    path('logout/', LogoutView.as_view(), name='logout'), #agregada ruta de cierre de sesión
]
