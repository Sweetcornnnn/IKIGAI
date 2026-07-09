from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.apps import apps
from django.db import models as django_models
from django.contrib.auth import authenticate, login, logout
import json
from datetime import datetime, timedelta

# Import models used in the admin dashboard
from apps.tasks.models import Task
from apps.habits.models import Habit, HabitLog
from apps.gamification.models import Achievement, UserAchievement
from apps.notifications.models import Notification
from apps.accounts.models import Profile
from apps.goals.models import Goal

# ─── ADMIN_MODELS Configuration ──────────────────────────────────────────────
ADMIN_MODELS = {
    'users': {
        'model': User,
        'label': 'Users',
        'icon': '👤',
        'search_fields': ['username', 'email', 'first_name', 'last_name'],
        'list_display': ['username', 'email', 'is_active', 'is_staff', 'date_joined'],
        'list_filter': ['is_active', 'is_staff', 'is_superuser'],
        'editable_fields': ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff'],
        'hidden_fields': ['password', 'last_login'],
    },
    'profiles': {
        'model': 'accounts.Profile',
        'label': 'Profiles',
        'icon': '👤',
        'search_fields': ['user__username', 'bio'],
        'list_display': ['user', 'xp', 'level', 'streak_days', 'created_at'],
        'list_filter': ['level'],
        'editable_fields': ['avatar', 'bio', 'xp', 'level', 'streak_days'],
    },
    'tasks': {
        'model': 'tasks.Task',
        'label': 'Tasks',
        'icon': '📋',
        'search_fields': ['title', 'description', 'user__username'],
        'list_display': ['title', 'user', 'category', 'priority', 'status', 'created_at'],
        'list_filter': ['category', 'priority', 'status', 'created_at'],
        'editable_fields': ['title', 'description', 'category', 'priority', 'status', 'due_date', 'xp_reward'],
    },
    'habits': {
        'model': 'habits.Habit',
        'label': 'Habits',
        'icon': '🌱',
        'search_fields': ['name', 'user__username'],
        'list_display': ['name', 'user', 'icon', 'active', 'created_at'],
        'list_filter': ['active', 'created_at'],
        'editable_fields': ['name', 'icon', 'active'],
    },
    'habitlogs': {
        'model': 'habits.HabitLog',
        'label': 'Habit Logs',
        'icon': '📊',
        'search_fields': ['habit__name', 'user__username'],
        'list_display': ['habit', 'user', 'date', 'completed'],
        'list_filter': ['date', 'completed'],
        'editable_fields': ['date', 'completed'],
    },
    'goals': {
        'model': 'goals.Goal',
        'label': 'Goals',
        'icon': '🎯',
        'search_fields': ['title', 'description', 'user__username'],
        'list_display': ['title', 'user', 'category', 'completed', 'created_at'],
        'list_filter': ['category', 'completed', 'created_at'],
        'editable_fields': ['emoji', 'title', 'description', 'category', 'completed'],
    },
    'achievements': {
        'model': 'gamification.Achievement',
        'label': 'Achievements',
        'icon': '🏆',
        'search_fields': ['name', 'description'],
        'list_display': ['name', 'category', 'requirement_type', 'requirement_value', 'xp_reward'],
        'list_filter': ['category', 'requirement_type'],
        'editable_fields': ['name', 'description', 'icon', 'category', 'requirement_type', 'requirement_value', 'xp_reward', 'order'],
    },
    'userachievements': {
        'model': 'gamification.UserAchievement',
        'label': 'User Achievements',
        'icon': '🎖️',
        'search_fields': ['user__username', 'achievement__name'],
        'list_display': ['user', 'achievement', 'unlocked_at'],
        'list_filter': ['unlocked_at'],
        'editable_fields': ['user', 'achievement'],
    },
    'notifications': {
        'model': 'notifications.Notification',
        'label': 'Notifications',
        'icon': '🔔',
        'search_fields': ['title', 'message', 'user__username'],
        'list_display': ['title', 'user', 'type', 'is_read', 'created_at'],
        'list_filter': ['type', 'is_read', 'created_at'],
        'editable_fields': ['type', 'title', 'message', 'link', 'is_read'],
    },
}


# ─── Helper Functions ──────────────────────────────────────────────────────

def get_model_class(model_key):
    """Get the model class from the model key"""
    config = ADMIN_MODELS.get(model_key)
    if not config:
        return None
    model_path = config['model']
    if isinstance(model_path, str):
        app_label, model_name = model_path.split('.')
        return apps.get_model(app_label, model_name)
    return model_path


def is_admin(user):
    return user.is_authenticated and user.is_superuser


# ─── Admin Views ─────────────────────────────────────────────────────────────

@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_dashboard(request):
    """Main admin dashboard"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    staff_users = User.objects.filter(is_staff=True).count()

    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='COMPLETED').count()
    pending_tasks = Task.objects.filter(status='PENDING').count()
    overdue_tasks = Task.objects.filter(status='PENDING', due_date__lt=today).count()

    total_habits = Habit.objects.filter(active=True).count()
    habit_logs = HabitLog.objects.filter(date=today, completed=True).count()

    total_achievements = Achievement.objects.count()
    unlocked_achievements = UserAchievement.objects.count()

    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()

    # Recent activity
    recent_activities = []
    recent_users = User.objects.order_by('-date_joined')[:5]
    for u in recent_users:
        recent_activities.append({
            'type': 'user_joined',
            'title': f'New user registered: {u.username}',
            'time': u.date_joined,
            'icon': '👤'
        })
    recent_tasks = Task.objects.filter(status='COMPLETED').order_by('-completed_at')[:5]
    for t in recent_tasks:
        if t.completed_at:
            recent_activities.append({
                'type': 'task_completed',
                'title': f'Task completed: {t.title} by {t.user.username}',
                'time': t.completed_at,
                'icon': '✅'
            })
    recent_ach = UserAchievement.objects.order_by('-unlocked_at')[:5]
    for ua in recent_ach:
        recent_activities.append({
            'type': 'achievement',
            'title': f'Achievement unlocked: {ua.achievement.name} by {ua.user.username}',
            'time': ua.unlocked_at,
            'icon': '🏆'
        })
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]

    context = {
        'total_users': total_users,
        'new_users_week': new_users_week,
        'staff_users': staff_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'total_habits': total_habits,
        'habit_logs': habit_logs,
        'total_achievements': total_achievements,
        'unlocked_achievements': unlocked_achievements,
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'recent_activities': recent_activities,
    }
    return render(request, 'admin_dashboard/index.html', context)


def admin_login(request):
    """Custom admin login page (hidden entry)"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard:dashboard')
        else:
            return redirect('dashboard:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard:dashboard')
        elif user is not None:
            messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'admin_dashboard/login.html')


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_logout(request):
    logout(request)
    return redirect('admin_dashboard:login')


def admin_check(request):
    """Check if current user is admin (AJAX)"""
    is_admin_user = request.user.is_authenticated and request.user.is_superuser
    return JsonResponse({'is_admin': is_admin_user})


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_dashboard/users.html', {'users': users})


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_toggle_user(request, user_id):
    if request.method != 'POST':
        return redirect('admin_dashboard:users')
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, 'Cannot modify superuser status.')
        return redirect('admin_dashboard:users')
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} {status}.')
    return redirect('admin_dashboard:users')


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_system(request):
    import django
    context = {
        'django_version': django.get_version(),
        'now': timezone.now(),
    }
    return render(request, 'admin_dashboard/system.html', context)


# ─── Model CRUD Views ──────────────────────────────────────────────────────

@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_model_list(request, model_name):
    config = ADMIN_MODELS.get(model_name)
    if not config:
        messages.error(request, f'Model "{model_name}" not found.')
        return redirect('admin_dashboard:dashboard')

    model_class = get_model_class(model_name)
    if not model_class:
        messages.error(request, f'Model "{model_name}" not found.')
        return redirect('admin_dashboard:dashboard')

    queryset = model_class.objects.all()

    search_query = request.GET.get('q', '')
    if search_query and config.get('search_fields'):
        search_conditions = Q()
        for field in config['search_fields']:
            search_conditions |= Q(**{f'{field}__icontains': search_query})
        queryset = queryset.filter(search_conditions)

    for filter_field in config.get('list_filter', []):
        filter_value = request.GET.get(f'filter_{filter_field}')
        if filter_value:
            queryset = queryset.filter(**{filter_field: filter_value})

    order_by = request.GET.get('order_by', '-created_at' if hasattr(model_class, 'created_at') else 'id')
    if order_by.startswith('-'):
        queryset = queryset.order_by(order_by)
        order_field = order_by[1:]
        order_direction = 'desc'
    else:
        queryset = queryset.order_by(order_by)
        order_field = order_by
        order_direction = 'asc'

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    filter_options = {}
    for filter_field in config.get('list_filter', []):
        field = model_class._meta.get_field(filter_field)
        choices = []
        if field.choices:
            choices = field.choices
        else:
            distinct_values = model_class.objects.values_list(filter_field, flat=True).distinct()
            choices = [(v, v) for v in distinct_values if v is not None]
        filter_options[filter_field] = choices

    context = {
        'model_name': model_name,
        'config': config,
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_options': filter_options,
        'order_by': order_by,
        'order_field': order_field,
        'order_direction': order_direction,
    }
    return render(request, 'admin_dashboard/model_list.html', context)


# ─── FIXED: admin_model_add ────────────────────────────────────────────────

@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_model_add(request, model_name):
    """Add a new record with proper date and empty field handling"""
    config = ADMIN_MODELS.get(model_name)
    if not config:
        messages.error(request, f'Model "{model_name}" not found.')
        return redirect('admin_dashboard:dashboard')

    model_class = get_model_class(model_name)
    if not model_class:
        messages.error(request, f'Model "{model_name}" not found.')
        return redirect('admin_dashboard:dashboard')

    if request.method == 'POST':
        try:
            instance = model_class()
            editable_fields = config.get('editable_fields', [])

            for field in editable_fields:
                value = request.POST.get(field)
                field_obj = model_class._meta.get_field(field)

                # --- Handle empty values ---
                if value == '':
                    if isinstance(field_obj, (django_models.TextField, django_models.CharField)):
                        value = ''  # empty string for text fields
                    else:
                        value = None
                elif value is None:
                    value = None

                # --- Parse based on field type ---
                if value is not None:
                    if isinstance(field_obj, (django_models.DateField, django_models.DateTimeField)):
                        date_formats = ['%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%d/%m/%Y']
                        parsed = None
                        for fmt in date_formats:
                            try:
                                parsed = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        if parsed:
                            if isinstance(field_obj, django_models.DateField):
                                instance.__setattr__(field, parsed.date())
                            else:
                                instance.__setattr__(field, parsed)
                    elif isinstance(field_obj, django_models.BooleanField):
                        instance.__setattr__(field, value == 'on')
                    elif isinstance(field_obj, (django_models.ForeignKey, django_models.OneToOneField)):
                        if value:
                            instance.__setattr__(field, field_obj.related_model.objects.get(id=value))
                    else:
                        instance.__setattr__(field, value)
                else:
                    # For NULL values
                    if field_obj.null:
                        instance.__setattr__(field, None)
                    elif isinstance(field_obj, (django_models.TextField, django_models.CharField)):
                        instance.__setattr__(field, '')
                    # else let Django's default handle it

            instance.save()
            messages.success(request, f'{config["label"]} added successfully!')
            return redirect('admin_dashboard:model_list', model_name=model_name)
        except Exception as e:
            messages.error(request, f'Error adding record: {str(e)}')

    # GET request: build form context
    foreign_key_options = {}
    for field in config.get('editable_fields', []):
        field_obj = model_class._meta.get_field(field)
        if isinstance(field_obj, (django_models.ForeignKey, django_models.OneToOneField)):
            foreign_key_options[field] = field_obj.related_model.objects.all()

    context = {
        'model_name': model_name,
        'config': config,
        'foreign_key_options': foreign_key_options,
        'action': 'Add',
    }
    return render(request, 'admin_dashboard/model_form.html', context)


# ─── FIXED: admin_model_edit ───────────────────────────────────────────────

@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_model_edit(request, model_name, pk):
    """Edit an existing record with proper date and empty field handling"""
    config = ADMIN_MODELS.get(model_name)
    if not config:
        messages.error(request, f'Model "{model_name}" not found.')
        return redirect('admin_dashboard:dashboard')

    model_class = get_model_class(model_name)
    if not model_class:
        messages.error(request, f'Model "{model_name}" not found.')
        return redirect('admin_dashboard:dashboard')

    instance = get_object_or_404(model_class, pk=pk)

    if request.method == 'POST':
        try:
            editable_fields = config.get('editable_fields', [])

            for field in editable_fields:
                value = request.POST.get(field)
                field_obj = model_class._meta.get_field(field)

                # --- Handle empty values ---
                if value == '':
                    if isinstance(field_obj, (django_models.TextField, django_models.CharField)):
                        value = ''  # empty string for text fields
                    else:
                        value = None
                elif value is None:
                    value = None

                # --- Parse based on field type ---
                if value is not None:
                    if isinstance(field_obj, (django_models.DateField, django_models.DateTimeField)):
                        date_formats = ['%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%d/%m/%Y']
                        parsed = None
                        for fmt in date_formats:
                            try:
                                parsed = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        if parsed:
                            if isinstance(field_obj, django_models.DateField):
                                instance.__setattr__(field, parsed.date())
                            else:
                                instance.__setattr__(field, parsed)
                    elif isinstance(field_obj, django_models.BooleanField):
                        instance.__setattr__(field, value == 'on')
                    elif isinstance(field_obj, (django_models.ForeignKey, django_models.OneToOneField)):
                        if value:
                            instance.__setattr__(field, field_obj.related_model.objects.get(id=value))
                    else:
                        instance.__setattr__(field, value)
                else:
                    # For NULL values
                    if field_obj.null:
                        instance.__setattr__(field, None)
                    elif isinstance(field_obj, (django_models.TextField, django_models.CharField)):
                        instance.__setattr__(field, '')
                    # else let Django's default handle it

            instance.save()
            messages.success(request, f'{config["label"]} updated successfully!')
            return redirect('admin_dashboard:model_list', model_name=model_name)
        except Exception as e:
            messages.error(request, f'Error updating record: {str(e)}')

    # GET request: build form context
    foreign_key_options = {}
    current_values = {}
    for field in config.get('editable_fields', []):
        field_obj = model_class._meta.get_field(field)
        if isinstance(field_obj, (django_models.ForeignKey, django_models.OneToOneField)):
            foreign_key_options[field] = field_obj.related_model.objects.all()
            current_values[field] = getattr(instance, field).id if getattr(instance, field) else None

    context = {
        'model_name': model_name,
        'config': config,
        'instance': instance,
        'foreign_key_options': foreign_key_options,
        'current_values': current_values,
        'action': 'Edit',
    }
    return render(request, 'admin_dashboard/model_form.html', context)


# ─── Delete and Bulk Action ──────────────────────────────────────────────────

@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_model_delete(request, model_name, pk):
    """Delete a record with confirmation"""
    config = ADMIN_MODELS.get(model_name)
    if not config:
        return JsonResponse({'error': 'Model not found'}, status=404)

    model_class = get_model_class(model_name)
    if not model_class:
        return JsonResponse({'error': 'Model not found'}, status=404)

    instance = get_object_or_404(model_class, pk=pk)

    if request.method == 'POST':
        try:
            instance.delete()
            messages.success(request, f'{config["label"]} deleted successfully!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # GET request - return JSON for modal
    return JsonResponse({
        'id': instance.id,
        'name': str(instance),
        'model_name': model_name,
        'model_label': config['label'],
    })


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_bulk_action(request, model_name):
    """Perform bulk actions on selected records"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    config = ADMIN_MODELS.get(model_name)
    if not config:
        return JsonResponse({'error': 'Model not found'}, status=404)

    model_class = get_model_class(model_name)
    if not model_class:
        return JsonResponse({'error': 'Model not found'}, status=404)

    action = request.POST.get('action')
    ids = request.POST.getlist('ids[]')

    if not ids:
        return JsonResponse({'error': 'No records selected'}, status=400)

    try:
        if action == 'delete':
            count = model_class.objects.filter(id__in=ids).delete()[0]
            messages.success(request, f'Deleted {count} {config["label"].lower()}')
            return JsonResponse({'success': True, 'count': count})
        elif action == 'mark_read':
            count = model_class.objects.filter(id__in=ids).update(is_read=True)
            messages.success(request, f'Marked {count} notifications as read')
            return JsonResponse({'success': True, 'count': count})
        elif action == 'mark_active':
            count = model_class.objects.filter(id__in=ids).update(active=True)
            messages.success(request, f'Activated {count} items')
            return JsonResponse({'success': True, 'count': count})
        elif action == 'mark_inactive':
            count = model_class.objects.filter(id__in=ids).update(active=False)
            messages.success(request, f'Deactivated {count} items')
            return JsonResponse({'success': True, 'count': count})
        else:
            return JsonResponse({'error': f'Unknown action: {action}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)