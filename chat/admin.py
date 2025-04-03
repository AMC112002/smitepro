from django.contrib import admin
from .models import ChatRoom, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'get_participants')
    inlines = [MessageInline]
    
    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message)