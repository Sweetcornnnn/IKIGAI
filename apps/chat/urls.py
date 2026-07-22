from django.urls import path
from . import views

app_name = 'apps.chat'

urlpatterns = [
    # Public chat
    path('send/', views.send_message, name='send'),
    path('messages/', views.get_messages, name='messages'),
    path('users/', views.get_users, name='users'),

    # Private chat
    path('private/<int:user_id>/', views.get_private_messages, name='private_messages'),
    path('private/send/', views.send_private_message, name='send_private'),
]