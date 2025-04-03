from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_rooms, name='chat_rooms'),
    path('create/', views.create_chat_room, name='create_chat_room'),
    path('<int:room_id>/', views.chat_room, name='chat_room'),
    path('api/messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('api/send-message/<int:room_id>/', views.send_message, name='send_message'),
]