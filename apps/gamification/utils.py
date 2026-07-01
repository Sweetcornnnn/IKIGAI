from django.utils import timezone
from apps.notifications.utils import create_notification
from .models import Achievement, UserAchievement
from apps.habits.models import Habit, HabitLog
from apps.tasks.models import Task
from apps.goals.models import Goal


def update_streak(user):
    """
    Update user's streak when they complete a task.
    Returns True if a milestone was reached.
    """
    profile = user.profile
    today = timezone.now().date()

    if profile.last_activity_date == today:
        return False

    if profile.last_activity_date == today - timezone.timedelta(days=1):
        profile.streak_days += 1
    else:
        profile.streak_days = 1

    profile.last_activity_date = today
    profile.save()

    milestones = [3, 7, 14, 21, 30, 60, 100]
    if profile.streak_days in milestones:
        create_notification(
            user=user,
            notification_type='STREAK',
            title=f'🔥 {profile.streak_days}-Day Streak!',
            message=f'You\'ve completed tasks for {profile.streak_days} days in a row! Keep going!',
            link='/accounts/profile/'
        )
        return True

    check_achievements(user)
    return False


def get_streak_status(user):
    profile = user.profile
    today = timezone.now().date()

    if profile.last_activity_date == today:
        status = 'active'
        message = f'{profile.streak_days} day streak! 🔥'
    elif profile.last_activity_date == today - timezone.timedelta(days=1):
        status = 'at_risk'
        message = 'Complete a task today to keep your streak alive! ⚠️'
    elif profile.streak_days > 0:
        status = 'broken'
        message = f'Streak broken at {profile.streak_days} days. Start a new one! 💪'
    else:
        status = 'none'
        message = 'Complete a task to start your streak! 🚀'

    return {
        'status': status,
        'message': message,
        'streak_days': profile.streak_days,
    }


def check_achievements(user):
    """
    Check all achievements and unlock any that are eligible
    Returns list of newly unlocked achievements
    """
    unlocked = []
    all_achievements = Achievement.objects.all()
    unlocked_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)

    for achievement in all_achievements:
        if achievement.id in unlocked_ids:
            continue

        is_unlocked, progress = achievement.check_unlock(user)

        if is_unlocked:
            UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )

            profile = user.profile
            profile.xp += achievement.xp_reward

            new_level = (profile.xp // 100) + 1
            if new_level > profile.level:
                profile.level = new_level

            profile.save()

            create_notification(
                user=user,
                notification_type='ACHIEVEMENT',
                title=f'🏆 Achievement Unlocked: {achievement.name}',
                message=f'You earned {achievement.xp_reward} XP for {achievement.description}',
                link='/accounts/achievements/'
            )

            unlocked.append(achievement)

    return unlocked


def get_user_achievements(user):
    """
    Get all achievements with unlock status for a user
    """
    unlocked_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
    profile = user.profile

    achievements = []
    for achievement in Achievement.objects.all():
        is_unlocked = achievement.id in unlocked_ids
        progress = 0
        required = achievement.requirement_value

        if is_unlocked:
            progress = required
        else:
            req_type = achievement.requirement_type
            if req_type == 'TASKS_COMPLETED':
                progress = user.tasks.filter(status='COMPLETED').count()
            elif req_type == 'STREAK_DAYS':
                progress = profile.streak_days
            elif req_type == 'LEVEL_REACHED':
                progress = profile.level
            elif req_type == 'XP_EARNED':
                progress = profile.xp
            elif req_type == 'HABITS_CREATED':
                progress = Habit.objects.filter(user=user, active=True).count()
            elif req_type == 'HABITS_COMPLETED':
                progress = HabitLog.objects.filter(user=user, completed=True).count()
            elif req_type == 'COMBO_ACHIEVEMENT':
                # Special case: return 1 if unlocked, else 0
                is_unlocked, progress = achievement.check_unlock(user)
                if is_unlocked:
                    progress = required
                else:
                    progress = 0
            elif req_type == 'PERFECT_DAY':
                is_unlocked, progress = achievement.check_unlock(user)
                if is_unlocked:
                    progress = required
                else:
                    progress = 0
            elif req_type == 'MORNING_PERSON':
                is_unlocked, progress = achievement.check_unlock(user)
                if is_unlocked:
                    progress = required
                else:
                    progress = 0

        achievements.append({
            'achievement': achievement,
            'unlocked': is_unlocked,
            'progress': min(progress, required),
            'required': required,
            'percentage': min(100, int((progress / required) * 100)) if required > 0 else 0,
        })

    return achievements


def get_unlocked_count(user):
    return UserAchievement.objects.filter(user=user).count()