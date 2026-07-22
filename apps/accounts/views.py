from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.utils import timezone
from apps.gamification.utils import get_user_achievements, get_unlocked_count
from apps.gamification.models import UserAchievement


def register(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'accounts/login.html')


def user_logout(request):
    """
    User logout view
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile(request):
    """
    User profile view
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    # Get achievements
    achievements = get_user_achievements(request.user)
    unlocked_count = get_unlocked_count(request.user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'achievements': achievements,
        'unlocked_count': unlocked_count,
        'total_count': len(achievements),
        'today': timezone.now().date(),
        'yesterday': timezone.now().date() - timezone.timedelta(days=1),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def achievements(request):
    """
    View all achievements with progress
    """
    achievements = get_user_achievements(request.user)
    unlocked_count = get_unlocked_count(request.user)

    context = {
        'achievements': achievements,
        'unlocked_count': unlocked_count,
        'total_count': len(achievements),
    }
    return render(request, 'accounts/achievements.html', context)


# ─── NEW: Profile API Endpoint for Chat ───
@login_required
def get_user_profile(request, user_id):
    """
    Get user profile data for the profile card (AJAX)
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile

        # Get achievements preview (up to 6)
        achievements = UserAchievement.objects.filter(
            user=user
        ).select_related('achievement')[:6]

        achievement_data = [
            {
                'icon': ua.achievement.icon,
                'name': ua.achievement.name,
            }
            for ua in achievements
        ]

        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'bio': profile.bio or '',
            'xp': profile.xp,
            'level': profile.level,
            'streak_days': profile.streak_days,
            'join_date': user.date_joined.strftime('%B %d, %Y'),
            'avatar': profile.get_avatar_url(),
            'achievements': achievement_data,
            'achievement_count': UserAchievement.objects.filter(user=user).count(),
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)