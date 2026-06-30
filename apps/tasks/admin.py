from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'category', 'priority', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'title', 'description', 'category', 'priority')
        }),
        ('Status', {
            'fields': ('status', 'due_date', 'completed_at')
        }),
        ('Gamification', {
            'fields': ('xp_reward',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_completed']

    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='COMPLETED', completed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} tasks marked as completed.')

    mark_as_completed.short_description = "Mark selected tasks as completed"