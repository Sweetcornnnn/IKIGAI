from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    """
    Task model for user productivity tracking
    """

    # Category choices (kept for backwards compatibility but not used in weekly view)
    CATEGORY_CHOICES = [
        ('WORK', 'Work'),
        ('PERSONAL', 'Personal'),
        ('HEALTH', 'Health'),
        ('LEARNING', 'Learning'),
        ('OTHER', 'Other'),
    ]

    # Priority choices
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
    ]

    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    # Task details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    # Dates
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Gamification
    xp_reward = models.IntegerField(default=10)

    def __str__(self):
        return self.title

    def mark_completed(self):
        """Mark task as completed and set completion time"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()

    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != 'COMPLETED':
            return self.due_date < timezone.now().date()
        return False

    def get_priority_with_icon(self):
        """Return priority with emoji"""
        icons = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢',
        }
        return f"{icons.get(self.priority, '')} {self.get_priority_display()}"

    class Meta:
        ordering = ['-created_at']