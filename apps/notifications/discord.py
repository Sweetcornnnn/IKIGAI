import requests
from django.conf import settings
from django.utils import timezone


def send_discord_notification(
        title,
        message,
        color=0xC9A96E,
        fields=None,
        thumbnail_url=None,
        image_url=None,
        footer_text=None,
        footer_icon=None,
        author_name=None,
        author_icon=None,
        author_url=None,
):
    """
    Send a rich embed message to Discord via webhook with enhanced options.

    Args:
        title (str): Embed title
        message (str): Embed description
        color (int): Hex color for the embed
        fields (list): Optional list of dicts with "name", "value", "inline"
        thumbnail_url (str): URL for small thumbnail image (top right)
        image_url (str): URL for large banner image (bottom)
        footer_text (str): Footer text
        footer_icon (str): Footer icon URL
        author_name (str): Author name
        author_icon (str): Author icon URL
        author_url (str): Author URL
    """
    webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', None)
    if not webhook_url:
        print("Discord webhook URL not configured. Skipping notification.")
        return

    embed = {
        "title": title,
        "description": message,
        "color": color,
        "timestamp": timezone.now().isoformat(),
    }

    if fields:
        embed["fields"] = fields

    if thumbnail_url:
        embed["thumbnail"] = {"url": thumbnail_url}

    if image_url:
        embed["image"] = {"url": image_url}

    if footer_text:
        embed["footer"] = {"text": footer_text}
        if footer_icon:
            embed["footer"]["icon_url"] = footer_icon

    if author_name:
        embed["author"] = {"name": author_name}
        if author_icon:
            embed["author"]["icon_url"] = author_icon
        if author_url:
            embed["author"]["url"] = author_url

    data = {"embeds": [embed]}

    try:
        response = requests.post(webhook_url, json=data, timeout=5)
        response.raise_for_status()
        print(f"✅ Discord notification sent: {title}")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")