from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('check/', views.admin_check, name='check'),  # ← ADD THIS
    path('users/', views.admin_users, name='users'),
    path('users/<int:user_id>/toggle/', views.admin_toggle_user, name='toggle_user'),
    path('system/', views.admin_system, name='system'),
]