from .models import Notification
from django.contrib.auth.models import User

def create_notification(user, notification_type, title, message, link=None):
    """
    Create a notification for a user
    """
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        link=link
    )
    return notification

def get_unread_count(user):
    """
    Get count of unread notifications for a user
    """
    return Notification.objects.filter(user=user, is_read=False).count()

def mark_all_as_read(user):
    """
    Mark all notifications as read for a user
    """
    return Notification.objects.filter(user=user, is_read=False).update(is_read=True)