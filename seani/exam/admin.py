from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.db import models
from django.urls.resolvers import URLPattern

from .models import Stage, Exam, ExamModule, CustomExam, LoadCSV
from .views import create, load_csv


# ------------------------
from django.contrib import admin
from .models import HomeScreenSetting

@admin.register(HomeScreenSetting)
class HomeScreenSettingAdmin(admin.ModelAdmin):
    list_display = ('screen_name', 'is_active', 'display_date', 'display_time')
    list_editable = ('is_active',)
    readonly_fields = ('activate_button',)
    actions = ['set_as_active']

    def activate_button(self, obj):
        if not obj.is_active:
            return f'<a class="button" href="/admin/activate_screen/{obj.id}/">Activar</a>'
        return "Activa"
    activate_button.allow_tags = True
    activate_button.short_description = "Acción"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('activate_screen/<int:setting_id>/', self.admin_site.admin_view(self.activate_screen), name='activate_screen'),
        ]
        return custom_urls + urls

    def activate_screen(self, request, setting_id):
        from django.shortcuts import redirect, get_object_or_404
        setting = get_object_or_404(HomeScreenSetting, id=setting_id)
        HomeScreenSetting.objects.update(is_active=False)
        setting.is_active = True
        setting.save()
        self.message_user(request, f'Pantalla "{setting.get_screen_name_display()}" activada correctamente.')
        return redirect('/admin/exam/homescreensetting/')

# ------------------------



class ExamModuleInline(admin.TabularInline):
    model = ExamModule
    extra = 1

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['stage', 'month', 'year']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'score', 'career', 'stage']
    list_filter = ['career', 'stage']
    inlines = [ExamModuleInline]

    search_fields = ['user__email']