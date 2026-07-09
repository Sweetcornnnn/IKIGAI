from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.admin_dashboard, name='dashboard'),
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('check/', views.admin_check, name='check'),

    # User management
    path('users/', views.admin_users, name='users'),
    path('users/<int:user_id>/toggle/', views.admin_toggle_user, name='toggle_user'),

    # System
    path('system/', views.admin_system, name='system'),

    # Model CRUD
    path('models/<str:model_name>/', views.admin_model_list, name='model_list'),
    path('models/<str:model_name>/add/', views.admin_model_add, name='model_add'),
    path('models/<str:model_name>/<int:pk>/edit/', views.admin_model_edit, name='model_edit'),
    path('models/<str:model_name>/<int:pk>/delete/', views.admin_model_delete, name='model_delete'),
    path('models/<str:model_name>/bulk-action/', views.admin_bulk_action, name='bulk_action'),
]