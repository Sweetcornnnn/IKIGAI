from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.weekly, name='weekly'),
    path('add-weekly/', views.task_add_weekly, name='add_weekly'),
    path('toggle/<int:pk>/', views.task_toggle, name='toggle'),
]