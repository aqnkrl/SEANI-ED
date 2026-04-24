from django.urls import path
from . import views

app_name = 'analytics' # Esto es lo que permite el "analytics:" en el botón

urlpatterns = [
    path('dashboard/', views.analitica_view, name='dashboard'),
    path('graficar/<str:modelo>/', views.graficar_view, name='graficar'),
]