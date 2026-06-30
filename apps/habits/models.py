from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Habit(models.Model):
    """
    A habit that a user wants to track
    """
    ICON_CHOICES = [
        ('🌅', 'Sunrise'),
        ('🚿', 'Shower'),
        ('🚫', 'No'),
        ('📖', 'Reading'),
        ('🍷', 'No Alcohol'),
        ('💪', 'Workout'),
        ('🌙', 'Bedtime'),
        ('🧘', 'Meditation'),
        ('📝', 'Journal'),
        ('💧', 'Water'),
        ('🏃', 'Running'),
        ('🎯', 'Focus'),
        ('🧠', 'Learning'),
        ('💤', 'Sleep'),
        ('🥗', 'Healthy Eating'),
        ('📱', 'No Phone'),
        ('🎵', 'Music'),
        ('✍️', 'Writing'),
        ('🎨', 'Creative'),
        ('🏋️', 'Strength'),
        ('🧹', 'Clean'),
        ('🌳', 'Nature'),
        ('🙏', 'Gratitude'),
        ('💡', 'Idea'),
        ('⭐', 'Star'),
        ('🔥', 'Streak'),
        ('✅', 'Complete'),
        ('📊', 'Progress'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=10, choices=ICON_CHOICES, default='✅')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.icon} {self.name}"

    def get_logs_for_month(self, year, month):
        """Get all logs for this habit for a specific month"""
        start_date = timezone.datetime(year, month, 1).date()
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1).date()
        else:
            end_date = timezone.datetime(year, month + 1, 1).date()

        return self.logs.filter(date__gte=start_date, date__lt=end_date)

    def get_completion_count_for_month(self, year, month):
        """Get number of completed days for a specific month"""
        return self.get_logs_for_month(year, month).filter(completed=True).count()

    def get_streak(self):
        """Calculate current streak for this habit"""
        logs = self.logs.filter(completed=True).order_by('-date')
        if not logs:
            return 0

        streak = 0
        today = timezone.now().date()
        for log in logs:
            if log.date == today - timezone.timedelta(days=streak):
                streak += 1
            else:
                break
        return streak

    def get_longest_streak(self):
        """Calculate longest streak for this habit"""
        logs = self.logs.filter(completed=True).order_by('date')
        if not logs:
            return 0

        longest = 0
        current = 0
        prev_date = None

        for log in logs:
            if prev_date is None or log.date == prev_date + timezone.timedelta(days=1):
                current += 1
            else:
                current = 1
            longest = max(longest, current)
            prev_date = log.date

        return longest

    class Meta:
        ordering = ['name']


class HabitLog(models.Model):
    """
    Daily log for a habit - tracks whether it was completed on a specific day
    """
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['habit', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} - {self.date}: {'✅' if self.completed else '❌'}"