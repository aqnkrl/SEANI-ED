from django.urls import path

from . import views

app_name = 'exam'
urlpatterns = [
    path('', views.home, name='home'),
    path('home2/', views.home2, name='home2'),
    path('home3/', views.home3, name='home3'),
    path('module/<int:module_id>/question/', views.question, name='question'),
    path('module/<int:module_id>/question/<int:question_id>/', views.question, name='question'),
    path('module/<int:module_id>/save/', views.save_module, name='save'),
    path('save/', views.save_exam, name='save_exam'),
    path('results/', views.get_scores_with_modules, name="results"),
]