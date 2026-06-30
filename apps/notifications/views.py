from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification
from .utils import get_unread_count, mark_all_as_read


@login_required
def notification_list(request):
    """
    View all notifications for the current user
    """
    notifications = Notification.objects.filter(user=request.user)
    unread_count = get_unread_count(request.user)

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def notification_mark_read(request, pk):
    """
    Mark a single notification as read
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications:list')


@login_required
def notification_mark_all_read(request):
    """
    Mark all notifications as read
    """
    mark_all_as_read(request.user)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')


@login_required
def notification_unread_count(request):
    """
    AJAX endpoint to get unread notification count
    """
    count = get_unread_count(request.user)
    return JsonResponse({'count': count})