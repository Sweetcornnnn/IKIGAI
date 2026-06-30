from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.tasks.models import Task
from apps.notifications.utils import get_unread_count
from apps.gamification.utils import get_streak_status
from apps.habits.models import Habit, HabitLog
from apps.goals.models import Goal  # Added for goals


@login_required
def home(request):
    """
    Main dashboard view - users must be logged in
    """
    user = request.user
    profile = user.profile
    today = timezone.now().date()

    # --- Task Statistics ---
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, status='COMPLETED').count()
    pending_tasks = Task.objects.filter(user=user, status='PENDING').count()
    overdue_tasks = Task.objects.filter(
        user=user,
        status='PENDING',
        due_date__lt=today
    ).count()

    # Recent tasks (last 5)
    recent_tasks = Task.objects.filter(user=user).order_by('-created_at')[:5]

    # Unread notification count
    unread_count = get_unread_count(user)

    # Streak status
    streak_status = get_streak_status(user)

    # --- Chart Data: Last 7 days ---
    chart_labels = []
    chart_data = []

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_labels.append(date.strftime('%a %d'))

        # Count tasks completed on this day
        count = Task.objects.filter(
            user=user,
            status='COMPLETED',
            completed_at__date=date
        ).count()
        chart_data.append(count)

    # --- Calendar Data: Tasks for current month ---
    calendar_data = {}

    # Tasks with due dates in this month
    due_tasks = Task.objects.filter(
        user=user,
        due_date__month=today.month,
        due_date__year=today.year
    ).exclude(due_date=None)

    for task in due_tasks:
        date_str = task.due_date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        calendar_data[date_str].append({
            'task': task,
            'type': 'due'
        })

    # Tasks completed this month
    completed_this_month = Task.objects.filter(
        user=user,
        status='COMPLETED',
        completed_at__month=today.month,
        completed_at__year=today.year
    )

    for task in completed_this_month:
        if task.completed_at:
            date_str = task.completed_at.strftime('%Y-%m-%d')
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            calendar_data[date_str].append({
                'task': task,
                'type': 'completed'
            })

    # Count calendar tasks for the header
    calendar_tasks_count = sum(len(tasks) for tasks in calendar_data.values())

    # --- Activity Timeline ---
    recent_activity = []

    # Task completions
    recent_completions = Task.objects.filter(
        user=user,
        status='COMPLETED'
    ).order_by('-completed_at')[:10]

    for task in recent_completions:
        if task.completed_at:
            recent_activity.append({
                'type': 'task_completed',
                'title': f'Completed task: {task.title}',
                'time': task.completed_at,
                'icon': '✅',
                'link': '/tasks/',
            })

    # Achievement unlocks
    from apps.gamification.models import UserAchievement
    recent_achievements = UserAchievement.objects.filter(
        user=user
    ).order_by('-unlocked_at')[:5]

    for ua in recent_achievements:
        recent_activity.append({
            'type': 'achievement',
            'title': f'Unlocked: {ua.achievement.name}',
            'time': ua.unlocked_at,
            'icon': '🏆',
            'link': '/accounts/achievements/',
        })

    # Sort by time (most recent first)
    recent_activity.sort(key=lambda x: x['time'], reverse=True)
    recent_activity = recent_activity[:10]

    # --- Category Breakdown ---
    category_stats = {}
    for category, label in Task.CATEGORY_CHOICES:
        count = Task.objects.filter(user=user, category=category).count()
        completed = Task.objects.filter(user=user, category=category, status='COMPLETED').count()
        if count > 0 or completed > 0:
            category_stats[label] = {
                'total': count,
                'completed': completed,
                'percentage': int((completed / count) * 100) if count > 0 else 0,
            }

    # --- Habit Statistics ---
    total_habits = Habit.objects.filter(user=user, active=True).count()
    today_completed = HabitLog.objects.filter(
        user=user,
        date=today,
        completed=True
    ).count()

    # Today's habit completion percentage
    today_percentage = int((today_completed / total_habits) * 100) if total_habits > 0 else 0

    # Monthly habit progress (from first of month to today)
    first_day = today.replace(day=1)
    month_logs = HabitLog.objects.filter(
        user=user,
        date__gte=first_day,
        date__lte=today
    )
    total_possible = total_habits * today.day
    total_completed_habits = month_logs.filter(completed=True).count()
    month_percentage = int((total_completed_habits / total_possible) * 100) if total_possible > 0 else 0

    # Recent habit completions (last 5)
    recent_habit_logs = HabitLog.objects.filter(
        user=user,
        completed=True
    ).order_by('-date')[:5]

    # --- Goal Statistics (NEW) ---
    goals = Goal.objects.filter(user=user)
    total_goals = goals.count()
    completed_goals = goals.filter(completed=True).count()
    goal_completion_rate = int((completed_goals / total_goals) * 100) if total_goals > 0 else 0

    context = {
        'username': user.username,
        'email': user.email,
        'profile': profile,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
        'unread_count': unread_count,
        'streak_status': streak_status,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'calendar_data': calendar_data,
        'calendar_tasks_count': calendar_tasks_count,
        'today': today,
        'recent_activity': recent_activity,
        'category_stats': category_stats,
        # Habit stats
        'total_habits': total_habits,
        'today_completed': today_completed,
        'today_percentage': today_percentage,
        'month_percentage': month_percentage,
        'recent_habit_logs': recent_habit_logs,
        # Goal stats (NEW)
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'goal_completion_rate': goal_completion_rate,
    }
    return render(request, 'dashboard/home.html', context)