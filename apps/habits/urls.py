from django.urls import path
from . import views

app_name = 'habits'

urlpatterns = [
    path('', views.habit_list, name='list'),
    path('add/', views.habit_add, name='add'),
    path('<int:pk>/edit/', views.habit_edit, name='edit'),
    path('<int:pk>/delete/', views.habit_delete, name='delete'),
    path('toggle/', views.habit_toggle, name='toggle'),
    path('stats/', views.habit_stats, name='stats'),
]