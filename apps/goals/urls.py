from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('toggle/<int:pk>/', views.goal_toggle, name='toggle'),
    path('add/', views.goal_add, name='add'),
    path('<int:pk>/detail/', views.goal_detail, name='detail'),
    path('<int:pk>/update/', views.goal_update, name='update'),
    path('<int:pk>/delete/', views.goal_delete, name='delete'),
]