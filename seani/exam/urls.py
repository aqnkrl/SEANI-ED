from django.urls import path

from . import views

app_name = 'exam'
urlpatterns = [
    path('exam/', views.home, name='home'),
    path('exam/module/<int:module_id>/question/', views.question, name='question'),
    path('exam/module/<int:module_id>/question/<int:question_id>/', views.question, name='question'),
    path('exam/module/<int:module_id>/save/', views.save_module, name='save'),
    path('exam/save/', views.save_exam, name='save_exam'),
    
    #### Urls for Admin
    path('admin/exam/create/', views.create, name="create"),
    path('admin/exam/loadcsv/', views.load_csv, name="loadcsv"),
    path('admin/exam/results/', views.get_scores_with_modules, name="results"),
]