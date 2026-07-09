from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Goal(models.Model):
    """
    Goal model – a single goal that can be weekly, monthly, or annual.
    """
    CATEGORY_CHOICES = [
        ('WEEKLY', 'Weekly Goals'),
        ('MONTHLY', 'Monthly Goals'),
        ('ANNUAL', 'Annual Goals'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='WEEKLY')
    title = models.CharField(max_length=200)
    emoji = models.CharField(max_length=10, default='📌')
    description = models.TextField(blank=True, default='')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.emoji} {self.title}"

    def mark_completed(self):
        """Mark goal as completed and set completion time"""
        self.completed = True
        self.completed_at = timezone.now()
        self.save()

    def mark_incomplete(self):
        """Unmark goal as completed"""
        self.completed = False
        self.completed_at = None
        self.save()

    class Meta:
        ordering = ['order', 'created_at']