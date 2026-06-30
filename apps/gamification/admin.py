from django.contrib import admin
from .models import Achievement, UserAchievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'category', 'requirement_type', 'requirement_value', 'xp_reward', 'order']
    list_filter = ['category', 'requirement_type']
    search_fields = ['name', 'description']
    ordering = ['order', 'requirement_value']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon', 'category')
        }),
        ('Requirements', {
            'fields': ('requirement_type', 'requirement_value')
        }),
        ('Reward', {
            'fields': ('xp_reward',)
        }),
        ('Display', {
            'fields': ('order',)
        }),
    )


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'unlocked_at']
    list_filter = ['unlocked_at']
    search_fields = ['user__username', 'achievement__name']
    readonly_fields = ['unlocked_at']
    ordering = ['-unlocked_at']