from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Inline Profile in User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('avatar', 'bio', 'xp', 'level', 'streak_days', 'last_activity_date')
    readonly_fields = ('xp', 'level', 'streak_days', 'last_activity_date')

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register Profile separately (optional, since it's inline now)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'xp', 'level', 'streak_days', 'last_activity_date']
    list_filter = ['level']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']