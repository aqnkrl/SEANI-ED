from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.db import models
from django.urls.resolvers import URLPattern

from .models import Stage, Exam, ExamModule, CustomExam, LoadCSV
from .views import create, load_csv

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
