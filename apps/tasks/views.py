from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
import random
from .models import Task
from .forms import TaskForm
from apps.notifications.utils import create_notification
from apps.gamification.utils import check_achievements, update_streak

# Circumference for the progress ring (2 * pi * r where r = 25)
CIRCUMFERENCE = 157.08

def get_week_dates():
    """Get Monday and Sunday of the current week"""
    today = timezone.now().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_week_range(year, week):
    """Get Monday and Sunday of a specific week"""
    first_day_of_year = datetime(year, 1, 1).date()
    days_to_first_monday = (7 - first_day_of_year.weekday()) % 7
    first_monday = first_day_of_year + timedelta(days=days_to_first_monday)

    monday = first_monday + timedelta(weeks=week - 1)
    sunday = monday + timedelta(days=6)
    return monday, sunday


@login_required
def weekly(request):
    """
    Weekly task view - spreadsheet style with 7 columns
    """
    user = request.user
    today = timezone.now().date()

    # Get week offset from query params
    week_offset = int(request.GET.get('week', 0))

    # Calculate week start and end
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    sunday = monday + timedelta(days=6)

    # Generate all 7 days
    days = [monday + timedelta(days=i) for i in range(7)]
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Get all tasks for this week
    tasks = Task.objects.filter(
        user=user,
        due_date__gte=monday,
        due_date__lte=sunday
    )

    # Build data for each day
    weekly_data = []
    total_tasks = 0
    total_completed = 0

    for i, day in enumerate(days):
        day_tasks = tasks.filter(due_date=day)
        completed = day_tasks.filter(status='COMPLETED').count()
        total = day_tasks.count()
        percentage = int((completed / total) * 100) if total > 0 else 0

        # Calculate the offset for the progress ring
        # When percentage is 100%, offset should be 0 (full ring)
        # When percentage is 0%, offset should be 157.08 (empty ring)
        offset = ((100 - percentage) / 100) * CIRCUMFERENCE

        total_tasks += total
        total_completed += completed

        weekly_data.append({
            'day': day,
            'day_name': day_names[i],
            'tasks': day_tasks.order_by('priority', 'title'),
            'completed': completed,
            'total': total,
            'percentage': percentage,
            'offset': offset,  # ← ADDED: For the progress ring
            'not_done': total - completed,
        })

    # Weekly summary
    weekly_summary = {
        'total_tasks': total_tasks,
        'total_completed': total_completed,
        'total_not_done': total_tasks - total_completed,
        'completion_rate': int((total_completed / total_tasks) * 100) if total_tasks > 0 else 0,
    }

    # Priority breakdown
    high_tasks = tasks.filter(priority='HIGH').count()
    medium_tasks = tasks.filter(priority='MEDIUM').count()
    low_tasks = tasks.filter(priority='LOW').count()
    total_tasks_all = high_tasks + medium_tasks + low_tasks

    priority_breakdown = {
        'high': {
            'count': high_tasks,
            'percentage': int((high_tasks / total_tasks_all) * 100) if total_tasks_all > 0 else 0,
        },
        'medium': {
            'count': medium_tasks,
            'percentage': int((medium_tasks / total_tasks_all) * 100) if total_tasks_all > 0 else 0,
        },
        'low': {
            'count': low_tasks,
            'percentage': int((low_tasks / total_tasks_all) * 100) if total_tasks_all > 0 else 0,
        },
    }

    # Motivational quotes
    quotes = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
        ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
        ("The secret of getting ahead is getting started.", "Mark Twain"),
        ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
        ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
        ("What you get by achieving your goals is not as important as what you become by achieving your goals.",
         "Zig Ziglar"),
        ("The only impossible journey is the one you never begin.", "Tony Robbins"),
        ("If you can dream it, you can achieve it.", "Zig Ziglar"),
        ("The secret of change is to focus all of your energy not on fighting the old, but on building the new.",
         "Socrates"),
        ("He who moves not forward, goes backward.", "Johann Wolfgang von Goethe"),
        ("A journey of a thousand miles begins with a single step.", "Lao Tzu"),
        ("The harder you work for something, the greater you'll feel when you achieve it.", "Unknown"),
        ("It always seems impossible until it's done.", "Nelson Mandela"),
        ("The only place where success comes before work is in the dictionary.", "Vidal Sassoon"),
        ("The best revenge is massive success.", "Frank Sinatra"),
        ("Strive not to be a success, but rather to be of value.", "Albert Einstein"),
        ("Success is walking from failure to failure with no loss of enthusiasm.", "Winston Churchill"),
        ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ]

    random_quote = random.choice(quotes)

    context = {
        'weekly_data': weekly_data,
        'days': days,
        'week_offset': week_offset,
        'monday': monday,
        'sunday': sunday,
        'weekly_summary': weekly_summary,
        'priority_breakdown': priority_breakdown,
        'quote': random_quote,
        'form': TaskForm(),
    }

    return render(request, 'tasks/weekly.html', context)


@login_required
def task_add_weekly(request):
    """
    Add a new task with day selector for weekly view
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user

            # Set due_date based on the selected day
            day_index = int(form.cleaned_data['day'])
            today = timezone.now().date()
            monday = today - timedelta(days=today.weekday())
            due_date = monday + timedelta(days=day_index)
            task.due_date = due_date

            task.save()

            messages.success(request, f'Task "{task.title}" added successfully!')
            return JsonResponse({'success': True, 'redirect': '/tasks/weekly/'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'success': False}, status=405)


@login_required
def task_toggle(request, pk):
    """
    Toggle task completion status (AJAX)
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        if task.status == 'COMPLETED':
            # Uncomplete task
            task.status = 'PENDING'
            task.completed_at = None
            task.save()
            completed = False
        else:
            # Complete task
            task.mark_completed()

            # Update user's XP
            profile = request.user.profile
            profile.xp += task.xp_reward

            # Check if level up
            new_level = (profile.xp // 100) + 1
            if new_level > profile.level:
                profile.level = new_level
                # Create level up notification
                create_notification(
                    user=request.user,
                    notification_type='LEVEL_UP',
                    title=f'Level {new_level} Unlocked! 🎉',
                    message=f'You reached level {new_level} by completing tasks! Keep going!',
                    link='/accounts/profile/'
                )
            profile.save()

            # Update streak
            update_streak(request.user)

            # Check for achievements
            check_achievements(request.user)

            # Create task completion notification
            create_notification(
                user=request.user,
                notification_type='TASK_COMPLETED',
                title=f'Task Completed: {task.title} ✅',
                message=f'You earned {task.xp_reward} XP for completing "{task.title}"',
                link='/tasks/weekly/'
            )

            completed = True

        return JsonResponse({
            'success': True,
            'completed': completed,
            'xp': task.xp_reward if completed else 0,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)