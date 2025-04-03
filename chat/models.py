from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.name:
            return self.name
        return ', '.join([user.username for user in self.participants.all()])
    
    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    class Meta:
        ordering = ['timestamp']