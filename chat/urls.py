from django.urls import path, include

from . import views

urlpatterns = [
    path('chat', views.chat, name='chat'),
    path('chat/history', views.get_chat_history, name='chat_history'),
]