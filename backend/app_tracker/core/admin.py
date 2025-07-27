from django.contrib import admin
from .models import Task, Project


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'completed', 'user', 'created_at']
    list_filter = ['completed', 'created_at', 'user']
    search_fields = ['title', 'description']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description']
