from django.utils import timezone
from apps.notifications.utils import create_notification
from .models import Achievement, UserAchievement


def update_streak(user):
    """
    Update user's streak when they complete a task.
    Returns True if a milestone was reached.
    """
    profile = user.profile
    today = timezone.now().date()

    # If user already has activity today, don't update streak again
    if profile.last_activity_date == today:
        return False

    # Check if this is a consecutive day
    if profile.last_activity_date == today - timezone.timedelta(days=1):
        # Consecutive day - increment streak
        profile.streak_days += 1
    else:
        # Either first activity or streak broken - reset to 1
        profile.streak_days = 1

    # Update last activity date
    profile.last_activity_date = today
    profile.save()

    # Check for streak milestones
    milestones = [3, 7, 14, 30, 60, 100]
    if profile.streak_days in milestones:
        create_notification(
            user=user,
            notification_type='STREAK',
            title=f'🔥 {profile.streak_days}-Day Streak!',
            message=f'You\'ve completed tasks for {profile.streak_days} days in a row! Keep going!',
            link='/accounts/profile/'
        )
        return True

    # Check for streak achievements
    check_achievements(user)

    return False


def get_streak_status(user):
    """
    Get streak status for display
    """
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

    # Get all achievements
    all_achievements = Achievement.objects.all()

    # Get already unlocked achievement IDs for this user
    unlocked_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)

    for achievement in all_achievements:
        if achievement.id in unlocked_ids:
            continue  # Already unlocked

        is_unlocked, progress = achievement.check_unlock(user)

        if is_unlocked:
            # Unlock the achievement
            UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )

            # Add XP reward
            profile = user.profile
            profile.xp += achievement.xp_reward

            # Check if this unlocks a new level
            new_level = (profile.xp // 100) + 1
            if new_level > profile.level:
                profile.level = new_level
                # Level up notification will be handled elsewhere

            profile.save()

            # Create notification
            create_notification(
                user=user,
                notification_type='ACHIEVEMENT',
                title=f'🏆 Achievement Unlocked: {achievement.name}',
                message=f'You earned {achievement.xp_reward} XP for {achievement.description}',
                link='/accounts/profile/'
            )

            unlocked.append(achievement)

    return unlocked


def get_user_achievements(user):
    """
    Get all achievements with unlock status for a user
    """
    unlocked_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)

    achievements = []
    for achievement in Achievement.objects.all():
        is_unlocked = achievement.id in unlocked_ids
        is_unlocked, progress = achievement.check_unlock(user) if not is_unlocked else (True,
                                                                                        achievement.requirement_value)

        # Get progress for locked achievements
        if not is_unlocked:
            # Get progress based on requirement type
            profile = user.profile
            if achievement.requirement_type == 'TASKS_COMPLETED':
                progress = user.tasks.filter(status='COMPLETED').count()
            elif achievement.requirement_type == 'STREAK_DAYS':
                progress = profile.streak_days
            elif achievement.requirement_type == 'LEVEL_REACHED':
                progress = profile.level
            elif achievement.requirement_type == 'XP_EARNED':
                progress = profile.xp
            else:
                progress = 0

        achievements.append({
            'achievement': achievement,
            'unlocked': is_unlocked,
            'progress': min(progress, achievement.requirement_value),
            'required': achievement.requirement_value,
            'percentage': min(100, int((
                                                   progress / achievement.requirement_value) * 100)) if achievement.requirement_value > 0 else 0,
        })

    return achievements


def get_unlocked_count(user):
    """
    Get count of unlocked achievements for a user
    """
    return UserAchievement.objects.filter(user=user).count()