from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('achievements/', views.achievements, name='achievements'),

    # ─── NEW: Profile API ───
    path('profile/<int:user_id>/', views.get_user_profile, name='user_profile'),
]