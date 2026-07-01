from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Goal
from .forms import GoalForm
from apps.notifications.utils import create_notification
from apps.gamification.utils import check_achievements
from apps.habits.models import Habit, HabitLog


@login_required
def dashboard(request):
    """
    Goals dashboard with three columns and analytics section
    """
    user = request.user
    today = timezone.now().date()

    # ─── Goals Data ───
    weekly_goals = Goal.objects.filter(user=user, category='WEEKLY')
    monthly_goals = Goal.objects.filter(user=user, category='MONTHLY')
    annual_goals = Goal.objects.filter(user=user, category='ANNUAL')

    def get_stats(goals):
        total = goals.count()
        completed = goals.filter(completed=True).count()
        percentage = int((completed / total) * 100) if total > 0 else 0
        return {'total': total, 'completed': completed, 'percentage': percentage}

    weekly_stats = get_stats(weekly_goals)
    monthly_stats = get_stats(monthly_goals)
    annual_stats = get_stats(annual_goals)

    # Overall progress (all goals combined)
    all_goals = Goal.objects.filter(user=user)
    total_goals = all_goals.count()
    completed_goals = all_goals.filter(completed=True).count()
    overall_percentage = int((completed_goals / total_goals) * 100) if total_goals > 0 else 0
    goal_completion_rate = overall_percentage  # same as overall

    # ─── Monthly Habit Progress (for doughnut chart) ───
    first_day = today.replace(day=1)
    habits = Habit.objects.filter(user=user, active=True)
    total_habits = habits.count()

    # Completed habits this month
    logs_this_month = HabitLog.objects.filter(
        user=user,
        date__gte=first_day,
        date__lte=today
    )
    total_possible = total_habits * today.day
    total_completed_habits = logs_this_month.filter(completed=True).count()
    monthly_habit_percentage = int((total_completed_habits / total_possible) * 100) if total_possible > 0 else 0

    # ─── Habit Summary Table ───
    habit_summary = []
    for habit in habits:
        completed_count = habit.get_completion_count_for_month(today.year, today.month)
        success_rate = int((completed_count / today.day) * 100) if today.day > 0 else 0
        habit_summary.append({
            'habit': habit,
            'completed': completed_count,
            'total': today.day,
            'success_rate': success_rate,
            'current_streak': habit.get_streak(),
            'longest_streak': habit.get_longest_streak(),
        })

    # ─── Line Chart Data (daily completion rate for the month) ───
    days_in_month = today.day  # up to today
    chart_dates = []
    chart_data = []
    for day in range(1, days_in_month + 1):
        date = datetime(today.year, today.month, day).date()
        chart_dates.append(date.strftime('%b %d'))
        daily_logs = HabitLog.objects.filter(
            user=user,
            date=date,
            completed=True
        ).count()
        daily_percentage = int((daily_logs / total_habits) * 100) if total_habits > 0 else 0
        chart_data.append(daily_percentage)

    # ─── Context ───
    context = {
        'weekly_goals': weekly_goals,
        'monthly_goals': monthly_goals,
        'annual_goals': annual_goals,
        'weekly_stats': weekly_stats,
        'monthly_stats': monthly_stats,
        'annual_stats': annual_stats,
        'overall_percentage': overall_percentage,
        'completed_goals': completed_goals,
        'total_goals': total_goals,
        'goal_completion_rate': goal_completion_rate,  # fixed
        'monthly_habit_percentage': monthly_habit_percentage,
        'total_completed_habits': total_completed_habits,
        'total_possible': total_possible,
        'habit_summary': habit_summary,
        'chart_dates': chart_dates,
        'chart_data': chart_data,
        'today': today,
    }
    return render(request, 'goals/dashboard.html', context)


@login_required
def goal_toggle(request, pk):
    """
    Toggle goal completion status (AJAX)
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        if goal.completed:
            goal.mark_incomplete()
            completed = False
        else:
            goal.mark_completed()
            # XP and achievements
            profile = request.user.profile
            profile.xp += 15  # XP reward for completing a goal
            profile.save()
            check_achievements(request.user)
            create_notification(
                user=request.user,
                notification_type='ACHIEVEMENT',
                title=f'🎯 Goal Completed: {goal.title}',
                message=f'You completed "{goal.title}"! Keep going!',
                link='/goals/'
            )
            completed = True

        return JsonResponse({
            'success': True,
            'completed': completed,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def goal_add(request):
    """
    Add a new goal (AJAX)
    """
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return JsonResponse({
                'success': True,
                'goal': {
                    'id': goal.id,
                    'emoji': goal.emoji,
                    'title': goal.title,
                    'category': goal.category,
                    'completed': goal.completed,
                    'description': goal.description,
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'success': False}, status=405)


@login_required
def goal_detail(request, pk):
    """
    Get goal details for the modal (AJAX)
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    return JsonResponse({
        'id': goal.id,
        'emoji': goal.emoji,
        'title': goal.title,
        'description': goal.description or '',
        'category': goal.category,
        'completed': goal.completed,
    })


@login_required
def goal_update(request, pk):
    """
    Update goal description (AJAX)
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    description = request.POST.get('description', '')
    goal.description = description
    goal.save()
    return JsonResponse({'success': True, 'description': description})


@login_required
def goal_delete(request, pk):
    """
    Delete a goal (AJAX)
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)