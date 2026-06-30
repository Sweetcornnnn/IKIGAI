from django.contrib import admin
from .models import Habit, HabitLog

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'icon', 'name', 'active', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['name', 'user__username']
    list_editable = ['active']
    ordering = ['user', 'name']

@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ['habit', 'user', 'date', 'completed']
    list_filter = ['completed', 'date']
    search_fields = ['habit__name', 'user__username']
    list_editable = ['completed']
    ordering = ['-date']