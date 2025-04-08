from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Max, OuterRef, Subquery
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models import ChatRoom, Message
from .forms import MessageForm
from django.db import models

@login_required
def chat_rooms(request):
    chat_rooms = ChatRoom.objects.filter(participants=request.user)
    
    latest_messages = Message.objects.filter(
        chat_room=OuterRef('pk')
    ).order_by('-timestamp')
    
    chat_rooms = chat_rooms.annotate(
        last_message=Subquery(latest_messages.values('content')[:1]),
        last_message_time=Subquery(latest_messages.values('timestamp')[:1])
    ).order_by('-last_message_time')
    
    return render(request, 'chat/chat_rooms.html', {
        'chat_rooms': chat_rooms
    })

@login_required
def create_chat_room(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        name = request.POST.get('name', '')
        
        if user_ids:
            users = User.objects.filter(id__in=user_ids)
            
            # Check if this is a one-on-one chat (only one other user)
            if len(user_ids) == 1:
                other_user_id = int(user_ids[0])
                other_user = get_object_or_404(User, id=other_user_id)
                
                # Buscar salas de chat que contengan exactamente a estos dos usuarios
                potential_rooms = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user)
                
                for room in potential_rooms:
                    # Verificar que la sala solo tiene estos dos participantes
                    if room.participants.count() == 2:
                        # Encontramos un chat individual existente, redirigir a él
                        return redirect('chat:chat_room', room_id=room.id)
            
            # Create new chat room if no duplicate found or it's a group chat
            chat_room = ChatRoom.objects.create(name=name)
            chat_room.participants.add(request.user, *users)
            
            return redirect('chat:chat_room', room_id=chat_room.id)
    
    users = User.objects.exclude(id=request.user.id)
    
    return render(request, 'chat/create_chat_room.html', {
        'users': users
    })

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    chat_messages = Message.objects.filter(chat_room=chat_room).order_by('timestamp')[:50]
    
    
    form = MessageForm()
    
    return render(request, 'chat/chat_room.html', {
        'chat_room': chat_room,
        'chat_messages': chat_messages,  
        'form': form
    })

@login_required
def get_messages(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    last_message_id = request.GET.get('last_id')
    
    messages = Message.objects.filter(chat_room=chat_room)
    
    if last_message_id:
        last_message = get_object_or_404(Message, id=last_message_id)
        messages = messages.filter(id__gt=last_message.id).order_by('timestamp')
    else:
        messages = messages.order_by('-timestamp')[:10] 
    
    Message.objects.filter(
        id__in=messages.filter(sender__in=chat_room.participants.exclude(id=request.user.id)).values_list('id', flat=True),
        is_read=False
    ).update(is_read=True)
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'sender_id': message.sender.id,
            'timestamp': message.timestamp.strftime('%d/%m/%Y %H:%M'),
            'is_self': message.sender.id == request.user.id
        })
    
    return JsonResponse({'messages': messages_data})

@login_required
def send_message(request, room_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message content is required'}, status=400)
        
        message = Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=content
        )
        
        chat_room.updated_at = timezone.now()
        chat_room.save()
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': message.sender.username,
                'sender_id': message.sender.id,
                'timestamp': message.timestamp.strftime('%d/%m/%Y %H:%M'),
                'is_self': True
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)