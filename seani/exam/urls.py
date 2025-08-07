from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views



app_name = 'exam'

urlpatterns = [
    # Vistas del aspirante
    path('exam/', views.home, name='home'),
    path('exam/home2/', views.home2, name='home2'),
    path('exam/home3/', views.home3, name='home3'),
    path('exam/module/<int:module_id>/question/', views.question, name='question'),
    path('exam/module/<int:module_id>/question/<int:question_id>/', views.question, name='question'),
    path('exam/module/<int:module_id>/save/', views.save_module, name='save'),
    path('exam/save/', views.save_exam, name='save_exam'),

    # Vistas del administrador
    path('admin/exam/create/', views.create, name="create"),
    path('admin/exam/loadcsv/', views.load_csv, name="loadcsv"),
    path('admin/exam/results/', views.get_scores_with_modules, name="results"),
    path('admin/exam/results/stage/', views.home_results, name='home_results'),

    # Vista para agregar etapa
    path('etapas/', views.stage_list, name='stage_list'),
    path('etapas/editar/<int:pk>/', views.stage_edit, name='stage_edit'),
    path('etapas/eliminar/<int:pk>/', views.stage_delete, name='stage_delete'),
    path('crear-etapa/', views.stage_add, name='stage_add'),

    # Pantallas de examen
    path('home-screens/', views.home_screen_table, name='home_screen_table'),

    # Exportación a Excel
    path('admin/exam/export/', views.export_scores_excel, name="export_scores_excel"),
    path('admin/exam/export/filtered/', views.export_filtered_results_excel, name="export_filtered_results_excel"),

    # Panel de administrador con gráficas generales
   # path('admin-home/', views.admin_home, name='admin_home'),
    path('admin-home/modulo-detalle/', views.detalle_por_modulo, name='detalle_por_modulo'),


    # Cierre de sesión
    path('logout/', LogoutView.as_view(), name='logout'),
]
