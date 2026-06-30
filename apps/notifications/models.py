from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """
    Notification model for user alerts and updates
    """

    # Notification types
    TYPE_CHOICES = [
        ('TASK_COMPLETED', 'Task Completed'),
        ('LEVEL_UP', 'Level Up'),
        ('ACHIEVEMENT', 'Achievement Unlocked'),
        ('STREAK', 'Streak Milestone'),
        ('REMINDER', 'Reminder'),
        ('SYSTEM', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SYSTEM')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, null=True)  # URL to navigate to
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()

    def time_ago(self):
        """Return human-readable time ago"""
        diff = timezone.now() - self.created_at
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"