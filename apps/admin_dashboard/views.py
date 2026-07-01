from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta
from apps.tasks.models import Task
from apps.habits.models import Habit, HabitLog
from apps.notifications.models import Notification
from apps.gamification.models import Achievement, UserAchievement
from django.http import JsonResponse

def admin_check(request):
    """Check if current user is admin (AJAX)"""
    is_admin = request.user.is_authenticated and request.user.is_superuser
    return JsonResponse({'is_admin': is_admin})


def is_admin(user):
    """Check if user is superuser/staff"""
    return user.is_authenticated and user.is_superuser


def admin_login(request):
    """Custom admin login page (hidden entry)"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard:dashboard')
        else:
            return redirect('dashboard:home')

    # Check if this is an admin login attempt
    if request.method == 'POST':
        from django.contrib.auth import authenticate
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
    """Admin logout"""
    logout(request)
    return redirect('admin_dashboard:login')


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_dashboard(request):
    """Main admin dashboard"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # User stats
    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    staff_users = User.objects.filter(is_staff=True).count()

    # Task stats
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='COMPLETED').count()
    pending_tasks = Task.objects.filter(status='PENDING').count()
    overdue_tasks = Task.objects.filter(status='PENDING', due_date__lt=today).count()

    # Habit stats
    total_habits = Habit.objects.filter(active=True).count()
    habit_logs = HabitLog.objects.filter(date=today, completed=True).count()

    # Achievement stats
    total_achievements = Achievement.objects.count()
    unlocked_achievements = UserAchievement.objects.count()

    # Recent activity
    recent_activities = []

    # Recent user registrations
    recent_users = User.objects.order_by('-date_joined')[:5]
    for user in recent_users:
        recent_activities.append({
            'type': 'user_joined',
            'title': f'New user registered: {user.username}',
            'time': user.date_joined,
            'icon': '👤'
        })

    # Recent task completions
    recent_tasks = Task.objects.filter(status='COMPLETED').order_by('-completed_at')[:5]
    for task in recent_tasks:
        if task.completed_at:
            recent_activities.append({
                'type': 'task_completed',
                'title': f'Task completed: {task.title} by {task.user.username}',
                'time': task.completed_at,
                'icon': '✅'
            })

    # Recent achievement unlocks
    recent_achievements = UserAchievement.objects.order_by('-unlocked_at')[:5]
    for ua in recent_achievements:
        recent_activities.append({
            'type': 'achievement',
            'title': f'Achievement unlocked: {ua.achievement.name} by {ua.user.username}',
            'time': ua.unlocked_at,
            'icon': '🏆'
        })

    # Sort by time
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]

    # System stats
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()

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


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_users(request):
    """Manage users"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_dashboard/users.html', {'users': users})


@user_passes_test(is_admin, login_url='admin_dashboard:login')
def admin_toggle_user(request, user_id):
    """Toggle user active status"""
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
    """System settings and info"""
    # Add system info here
    return render(request, 'admin_dashboard/system.html')