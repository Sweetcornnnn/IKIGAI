from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
import calendar as cal
from .models import Habit, HabitLog
from .forms import HabitForm
from apps.notifications.utils import create_notification
from apps.gamification.utils import check_achievements


@login_required
def habit_list(request):
    """
    Main habits page with monthly grid and stats
    """
    user = request.user

    # Get month/year from query params, default to current month
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Validate month/year
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Get first and last day of month
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    # Get all active habits for user
    habits = Habit.objects.filter(user=user, active=True)

    # Get all logs for this month
    logs = HabitLog.objects.filter(
        user=user,
        date__gte=first_day,
        date__lte=last_day
    )

    # Create a lookup dict for logs: (habit_id, date) -> completed
    log_lookup = {}
    for log in logs:
        log_lookup[(log.habit_id, log.date)] = log.completed

    # Build the grid data
    days_in_month = monthrange(year, month)[1]
    days = [datetime(year, month, day).date() for day in range(1, days_in_month + 1)]

    grid_data = []
    for habit in habits:
        habit_data = {
            'habit': habit,
            'days': []
        }
        for day in days:
            key = (habit.id, day)
            habit_data['days'].append({
                'date': day,
                'completed': log_lookup.get(key, False)
            })
        grid_data.append(habit_data)

    # Calculate statistics
    total_habits = habits.count()
    total_possible = total_habits * days_in_month
    total_completed = sum(1 for log in logs if log.completed)
    overall_percentage = int((total_completed / total_possible) * 100) if total_possible > 0 else 0

    # Per-habit stats
    habit_stats = []
    for habit in habits:
        completed_count = habit.get_completion_count_for_month(year, month)
        percentage = int((completed_count / days_in_month) * 100) if days_in_month > 0 else 0
        habit_stats.append({
            'habit': habit,
            'completed': completed_count,
            'total': days_in_month,
            'percentage': percentage,
            'streak': habit.get_streak(),
            'longest_streak': habit.get_longest_streak(),
        })

    # Current streak for today (all habits completed today?)
    today_completed = HabitLog.objects.filter(
        user=user,
        date=today,
        completed=True
    ).count()
    today_all_done = (today_completed == total_habits) if total_habits > 0 else False

    context = {
        'habits': habits,
        'grid_data': grid_data,
        'days': days,
        'year': year,
        'month': month,
        'month_name': datetime(year, month, 1).strftime('%B'),
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
        'total_habits': total_habits,
        'total_completed': total_completed,
        'total_possible': total_possible,
        'overall_percentage': overall_percentage,
        'habit_stats': habit_stats,
        'today_all_done': today_all_done,
        'today': today,
        'first_day': first_day,
        'last_day': last_day,
    }

    return render(request, 'habits/list.html', context)


@login_required
def habit_add(request):
    """
    Add a new habit
    """
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, f'Habit "{habit.name}" created successfully!')

            # Check for achievements
            check_achievements(request.user)

            return redirect('habits:list')
    else:
        form = HabitForm()

    return render(request, 'habits/add.html', {'form': form})


@login_required
def habit_edit(request, pk):
    """
    Edit an existing habit
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)

    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Habit "{habit.name}" updated successfully!')
            return redirect('habits:list')
    else:
        form = HabitForm(instance=habit)

    return render(request, 'habits/edit.html', {'form': form, 'habit': habit})


@login_required
def habit_delete(request, pk):
    """
    Delete a habit (soft delete by setting active=False)
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)

    if request.method == 'POST':
        habit.active = False
        habit.save()
        messages.success(request, f'Habit "{habit.name}" deleted successfully!')
        return redirect('habits:list')

    return render(request, 'habits/delete.html', {'habit': habit})


@login_required
def habit_toggle(request):
    """
    Toggle a habit for a specific day (AJAX)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    habit_id = request.POST.get('habit_id')
    date_str = request.POST.get('date')

    if not habit_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        habit = get_object_or_404(Habit, pk=habit_id, user=request.user)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Get or create log
        log, created = HabitLog.objects.get_or_create(
            habit=habit,
            user=request.user,
            date=date,
            defaults={'completed': True}
        )

        if not created:
            # Toggle the completion
            log.completed = not log.completed
            log.save()

        # Check for achievements when completing habits
        if log.completed:
            check_achievements(request.user)

            # Check if all habits for today are done
            habits_today = HabitLog.objects.filter(
                user=request.user,
                date=date,
                completed=True
            ).count()
            total_habits = Habit.objects.filter(user=request.user, active=True).count()

            if habits_today == total_habits and total_habits > 0:
                # All habits done today!
                create_notification(
                    user=request.user,
                    notification_type='ACHIEVEMENT',
                    title='All Habits Complete! 🎉',
                    message=f'You completed all your habits on {date.strftime("%B %d, %Y")}!',
                    link='/habits/'
                )

        return JsonResponse({
            'success': True,
            'completed': log.completed,
            'habit_name': habit.name,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def habit_stats(request):
    """
    View habit statistics and charts (AJAX data endpoint)
    """
    user = request.user
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    habits = Habit.objects.filter(user=user, active=True)

    # Get daily completion data for the month
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    # Daily completion percentage for the chart
    daily_data = []
    for day in range(1, monthrange(year, month)[1] + 1):
        date = datetime(year, month, day).date()
        completed = HabitLog.objects.filter(
            user=user,
            date=date,
            completed=True
        ).count()
        total = habits.count()
        percentage = int((completed / total) * 100) if total > 0 else 0
        daily_data.append({
            'day': day,
            'date': date.strftime('%b %d'),
            'percentage': percentage,
            'completed': completed,
            'total': total,
        })

    # Habit summary
    habit_summary = []
    total_possible = len(habits) * monthrange(year, month)[1]
    total_completed = 0

    for habit in habits:
        completed_count = habit.get_completion_count_for_month(year, month)
        total_completed += completed_count
        habit_summary.append({
            'name': habit.name,
            'icon': habit.icon,
            'completed': completed_count,
            'total': monthrange(year, month)[1],
            'percentage': int((completed_count / monthrange(year, month)[1]) * 100) if monthrange(year, month)[
                                                                                           1] > 0 else 0,
            'streak': habit.get_streak(),
            'longest_streak': habit.get_longest_streak(),
        })

    overall_percentage = int((total_completed / total_possible) * 100) if total_possible > 0 else 0

    return JsonResponse({
        'daily_data': daily_data,
        'habit_summary': habit_summary,
        'overall_percentage': overall_percentage,
        'total_completed': total_completed,
        'total_possible': total_possible,
        'total_habits': len(habits),
        'month_name': datetime(year, month, 1).strftime('%B %Y'),
    })