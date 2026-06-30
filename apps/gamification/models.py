from django.db import models
from django.contrib.auth.models import User


class Achievement(models.Model):
    """
    Achievement definition - what users can unlock
    """

    # Achievement categories
    CATEGORY_CHOICES = [
        ('TASKS', 'Task Master'),
        ('STREAK', 'Streak Warrior'),
        ('HABITS', 'Habit Builder'),
        ('LEVEL', 'Level Up'),
        ('SPECIAL', 'Special'),
    ]

    # Requirement types
    REQUIREMENT_CHOICES = [
        ('TASKS_COMPLETED', 'Number of tasks completed'),
        ('STREAK_DAYS', 'Consecutive days with activity'),
        ('LEVEL_REACHED', 'Reach a specific level'),
        ('XP_EARNED', 'Total XP earned'),
        ('HABITS_CREATED', 'Number of habits created'),
        ('HABITS_COMPLETED', 'Number of habits completed in a month'),
    ]

    # Basic info
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='TASKS')
    icon = models.CharField(max_length=50, default='🏆')  # Emoji icon

    # Requirements
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_CHOICES)
    requirement_value = models.IntegerField()

    # Reward
    xp_reward = models.IntegerField(default=50)

    # Ordering
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.icon} {self.name}"

    def check_unlock(self, user):
        """
        Check if a user has met the requirements for this achievement
        Returns (is_unlocked, progress)
        """
        profile = user.profile

        if self.requirement_type == 'TASKS_COMPLETED':
            completed = user.tasks.filter(status='COMPLETED').count()
            return completed >= self.requirement_value, completed

        elif self.requirement_type == 'STREAK_DAYS':
            return profile.streak_days >= self.requirement_value, profile.streak_days

        elif self.requirement_type == 'LEVEL_REACHED':
            return profile.level >= self.requirement_value, profile.level

        elif self.requirement_type == 'XP_EARNED':
            return profile.xp >= self.requirement_value, profile.xp

        return False, 0

    class Meta:
        ordering = ['order', 'requirement_value']
        verbose_name_plural = 'Achievements'


class UserAchievement(models.Model):
    """
    Track which achievements a user has unlocked
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']