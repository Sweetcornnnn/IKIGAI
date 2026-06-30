from django.contrib import admin
from .models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'emoji', 'title', 'category', 'completed', 'created_at']
    list_filter = ['category', 'completed', 'created_at']
    search_fields = ['title', 'user__username']
    list_editable = ['completed']
    ordering = ['-created_at']