from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'exam'
urlpatterns = [
    #path('', views.home, name='home'),
    path('exam/', views.home, name='home'),
    path('exam/home2/', views.home2, name='home2'),
    path('exam/home3/', views.home3, name='home3'),
    #path('module/<int:module_id>/question/', views.question, name='question'),
    path('exam/module/<int:module_id>/question/', views.question, name='question'),
    #path('module/<int:module_id>/question/<int:question_id>/', views.question, name='question'),
    path('exam/module/<int:module_id>/question/<int:question_id>/', views.question, name='question'),
    #path('module/<int:module_id>/save/', views.save_module, name='save'),
    path('exam/module/<int:module_id>/save/', views.save_module, name='save'),
    #path('save/', views.save_exam, name='save_exam'),
    path('exam/save/', views.save_exam, name='save_exam'),
    
    #### Urls for Admin
    path('admin/exam/create/', views.create, name="create"),
    path('admin/exam/loadcsv/', views.load_csv, name="loadcsv"),
    path('admin/exam/results/', views.get_scores_with_modules, name="results"),
    #path('results/', views.get_scores_with_modules, name="results"),
    path('admin/exam/results/stage/', views.home_results, name='home_results'),  # <-- Ruta nueva   

    path('logout/', LogoutView.as_view(), name='logout'),
 

]
