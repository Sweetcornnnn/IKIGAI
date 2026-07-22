from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import ChatMessage, ChatRoom
from django.utils import timezone
from datetime import timedelta


@login_required
def send_message(request):
    """Send a public message via POST"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    try:
        room, created = ChatRoom.objects.get_or_create(
            name='IKIGANTS',
            defaults={'slug': 'ikigants'}
        )

        chat_message = ChatMessage.objects.create(
            user=request.user,
            content=message,
            room=room,
            is_private=False
        )

        return JsonResponse({
            'success': True,
            'message': {
                'id': chat_message.id,
                'user_id': chat_message.user.id,
                'username': chat_message.user.username,
                'message': chat_message.content,
                'timestamp': chat_message.created_at.isoformat(),
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_messages(request):
    """Get recent public messages"""
    try:
        room = ChatRoom.objects.get(name='IKIGANTS')
        messages = ChatMessage.objects.filter(
            room=room,
            is_private=False
        ).order_by('-created_at')[:50]

        data = {
            'messages': [
                {
                    'id': msg.id,
                    'user_id': msg.user.id,
                    'username': msg.user.username,
                    'message': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                }
                for msg in reversed(messages)
            ]
        }
        return JsonResponse(data)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'messages': []})


@login_required
def get_users(request):
    """Get all users with online status (based on last activity)"""
    cutoff = timezone.now() - timedelta(minutes=5)
    users = User.objects.all()
    user_data = []

    for user in users:
        avatar_url = None
        try:
            if user.profile and user.profile.avatar:
                avatar_url = user.profile.avatar.url
        except:
            pass

        is_online = False
        if hasattr(user, 'profile') and user.profile.last_activity:
            is_online = user.profile.last_activity >= cutoff

        user_data.append({
            'id': user.id,
            'username': user.username,
            'avatar': avatar_url,
            'is_online': is_online,
        })

    return JsonResponse({'users': user_data})


# ─── NEW: Private Message Endpoints ───

@login_required
def get_private_messages(request, user_id):
    """Get private messages between current user and another user"""
    try:
        other_user = User.objects.get(id=user_id)
        current_user = request.user

        # Get or create the private room
        ids = sorted([current_user.id, other_user.id])
        room_name = f'DM_{ids[0]}_{ids[1]}'
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={'slug': room_name}
        )

        # Get messages for this room
        messages = ChatMessage.objects.filter(
            room=room,
            is_private=True
        ).order_by('-created_at')[:50]

        data = {
            'messages': [
                {
                    'id': msg.id,
                    'user_id': msg.user.id,
                    'username': msg.user.username,
                    'message': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                }
                for msg in reversed(messages)
            ]
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def send_private_message(request):
    """Send a private message to another user"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    message = request.POST.get('message', '').strip()
    recipient_id = request.POST.get('recipient_id')

    if not message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    if not recipient_id:
        return JsonResponse({'error': 'Recipient ID required'}, status=400)

    try:
        recipient = User.objects.get(id=recipient_id)
        current_user = request.user

        if recipient == current_user:
            return JsonResponse({'error': 'Cannot message yourself'}, status=400)

        # Get or create the private room
        ids = sorted([current_user.id, recipient.id])
        room_name = f'DM_{ids[0]}_{ids[1]}'
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={'slug': room_name}
        )

        chat_message = ChatMessage.objects.create(
            user=current_user,
            content=message,
            room=room,
            recipient=recipient,
            is_private=True
        )

        return JsonResponse({
            'success': True,
            'message': {
                'id': chat_message.id,
                'user_id': chat_message.user.id,
                'username': chat_message.user.username,
                'message': chat_message.content,
                'timestamp': chat_message.created_at.isoformat(),
            }
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'Recipient not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)