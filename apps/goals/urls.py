from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('toggle/<int:pk>/', views.goal_toggle, name='toggle'),
    path('add/', views.goal_add, name='add'),
    path('delete/<int:pk>/', views.goal_delete, name='delete'),
]