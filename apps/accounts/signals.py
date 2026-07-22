from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from apps.notifications.discord import send_discord_notification

@receiver(post_save, sender=User)
def send_new_user_discord_notification(sender, instance, created, **kwargs):
    """
    Send an extravagant Discord notification when a new user registers.
    """
    if created:
        # Get avatar URL if it exists
        avatar_url = None
        try:
            if instance.profile and instance.profile.avatar:
                if settings.DEBUG:
                    avatar_url = f"http://127.0.0.1:8000{instance.profile.avatar.url}"
                else:
                    avatar_url = f"https://yourdomain.com{instance.profile.avatar.url}"
        except:
            pass

        # Use a vibrant gold color
        color = 0xFFD700  # Gold

        # Send the extravagant notification
        send_discord_notification(
            title="🌟 **New Member Arrived!**",
            message=(
                f"🎉 **Please welcome {instance.username}** to the IKIGAI community!\n\n"
                "We're thrilled to have you on board. Get ready to track tasks, build habits, "
                "and unlock achievements. Your journey to purpose begins now! 💪"
            ),
            color=color,
            fields=[
                {"name": "👤 Username", "value": instance.username, "inline": True},
                {"name": "📧 Email", "value": instance.email or "No email provided", "inline": True},
                {"name": "📅 Joined", "value": instance.date_joined.strftime("%B %d, %Y at %I:%M %p"), "inline": True},
                {"name": "🎯 Next Step", "value": "Start your first task or habit today!", "inline": False},
            ],
            thumbnail_url=avatar_url if avatar_url else "https://ikigai.com/static/images/ikigai-logo.png",
            image_url="https://ikigai.com/static/images/welcome-banner.png",  # Optional: add a banner image
            footer_text="IKIGAI • Find Your Purpose",
            footer_icon="https://ikigai.com/static/images/ikigai-icon.png",
            author_name="IKIGAI Platform",
            author_icon="https://ikigai.com/static/images/ikigai-icon.png",
            author_url="https://ikigai.com/",
        )