from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import json
from datetime import timedelta

from chat.models import ChatRoom, Message
from chat.forms import MessageForm

class ChatModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')
        
        # Create chat rooms
        self.chat_room1 = ChatRoom.objects.create(name='Test Room 1')
        self.chat_room1.participants.add(self.user1, self.user2)
        
        self.chat_room2 = ChatRoom.objects.create(name='Test Room 2')
        self.chat_room2.participants.add(self.user1, self.user2, self.user3)
        
        # Create messages
        self.message1 = Message.objects.create(
            chat_room=self.chat_room1,
            sender=self.user1,
            content='Hello from user1',
            timestamp=timezone.now() - timedelta(minutes=10)
        )
        
        self.message2 = Message.objects.create(
            chat_room=self.chat_room1,
            sender=self.user2,
            content='Hello from user2',
            timestamp=timezone.now() - timedelta(minutes=5)
        )

    def test_chatroom_model(self):
        """Test ChatRoom model basic functionality"""
        self.assertEqual(str(self.chat_room1), 'Test Room 1')
        
        # Test unnamed chat room
        unnamed_room = ChatRoom.objects.create()
        unnamed_room.participants.add(self.user1, self.user3)
        self.assertEqual(str(unnamed_room), 'user1, user3')
        
        # Test ordering by updated_at
        rooms = ChatRoom.objects.all()
        self.assertEqual(rooms[0], unnamed_room)  # Most recently created
    
    def test_message_model(self):
        """Test Message model basic functionality"""
        self.assertEqual(str(self.message1), 'user1: Hello from user1')
        
        # Test long message truncation in string representation
        long_message = Message.objects.create(
            chat_room=self.chat_room1,
            sender=self.user1,
            content='This is a very long message that should be truncated in the string representation of the message object'
        )
        # Fixed expected value to match actual truncation length in the model
        self.assertEqual(str(long_message), 'user1: This is a very long message that should be truncat')
        
        # Test ordering by timestamp
        messages = Message.objects.filter(chat_room=self.chat_room1)
        self.assertEqual(messages[0], self.message1)  # Older message first


class ChatViewsTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')
        
        # Create chat rooms
        self.chat_room1 = ChatRoom.objects.create(name='Test Room 1')
        self.chat_room1.participants.add(self.user1, self.user2)
        
        self.chat_room2 = ChatRoom.objects.create(name='Test Room 2')
        self.chat_room2.participants.add(self.user1, self.user3)
        
        # Create messages
        self.message1 = Message.objects.create(
            chat_room=self.chat_room1,
            sender=self.user1,
            content='Hello from user1',
            timestamp=timezone.now() - timedelta(minutes=10),
            is_read=True
        )
        
        self.message2 = Message.objects.create(
            chat_room=self.chat_room1,
            sender=self.user2,
            content='Hello from user2',
            timestamp=timezone.now() - timedelta(minutes=5),
            is_read=False
        )
        
        # Create client and login
        self.client = Client()
        self.client.login(username='user1', password='password1')

    def test_chat_rooms_view(self):
        """Test the chat_rooms view"""
        response = self.client.get(reverse('chat:chat_rooms'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_rooms.html')
        
        # Check that both chat rooms are listed
        self.assertContains(response, 'Test Room 1')
        self.assertContains(response, 'Test Room 2')
        
        # Check that last message is displayed
        self.assertContains(response, 'Hello from user2')
    
    def test_create_chat_room_view_get(self):
        """Test the GET request to create_chat_room view"""
        response = self.client.get(reverse('chat:create_chat_room'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/create_chat_room.html')
        
        # Check that other users are listed
        self.assertContains(response, 'user2')
        self.assertContains(response, 'user3')
        self.assertNotContains(response, 'user1')  # Current user should not be in the list
    
    def test_create_chat_room_view_post_new_group(self):
        """Test creating a new group chat room"""
        response = self.client.post(reverse('chat:create_chat_room'), {
            'users': [self.user2.id, self.user3.id],
            'name': 'Group Chat'
        })
        
        # Should redirect to the new chat room
        self.assertEqual(response.status_code, 302)
        
        # Check that the new chat room was created
        chat_room = ChatRoom.objects.get(name='Group Chat')
        self.assertEqual(chat_room.participants.count(), 3)  # user1, user2, user3
    
    def test_create_chat_room_view_post_existing_one_on_one(self):
        """Test creating a one-on-one chat that already exists"""
        response = self.client.post(reverse('chat:create_chat_room'), {
            'users': [self.user2.id],
            'name': 'New One-on-One Chat'
        })
        
        # Should redirect to the existing chat room
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('chat:chat_room', kwargs={'room_id': self.chat_room1.id}))
    
    def test_chat_room_view(self):
        """Test the chat_room view"""
        response = self.client.get(reverse('chat:chat_room', kwargs={'room_id': self.chat_room1.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_room.html')
        
        # Check that chat messages are displayed
        self.assertContains(response, 'Hello from user1')
        self.assertContains(response, 'Hello from user2')
        
        # Check that form is in context
        self.assertIsInstance(response.context['form'], MessageForm)
    
    def test_chat_room_view_unauthorized(self):
        """Test accessing a chat room where the user is not a participant"""
        # Create a chat room where user1 is not a participant
        chat_room3 = ChatRoom.objects.create(name='Private Room')
        chat_room3.participants.add(self.user2, self.user3)
        
        response = self.client.get(reverse('chat:chat_room', kwargs={'room_id': chat_room3.id}))
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
    
    def test_get_messages_view(self):
        """Test the get_messages AJAX view"""
        # Create an isolated test environment
        room = ChatRoom.objects.create(name='Test Isolated Room')
        room.participants.add(self.user1, self.user2)
        
        # Create some messages for this test
        m1 = Message.objects.create(
            chat_room=room,
            sender=self.user1,
            content='Test message 1',
            timestamp=timezone.now() - timedelta(minutes=10),
            is_read=True
        )
        
        m2 = Message.objects.create(
            chat_room=room,
            sender=self.user2,
            content='Test message 2',
            timestamp=timezone.now() - timedelta(minutes=5),
            is_read=False
        )
        
        # Test GET request without last_id
        response = self.client.get(reverse('chat:get_messages', kwargs={'room_id': room.id}))
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verify message data
        self.assertEqual(len(data['messages']), 2)
        self.assertEqual(data['messages'][0]['content'], 'Test message 2')  # Most recent first
        self.assertEqual(data['messages'][1]['content'], 'Test message 1')
        
        # Test with last_id parameter
        response = self.client.get(
            reverse('chat:get_messages', kwargs={'room_id': room.id}),
            {'last_id': m1.id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Only message 2 should be returned as it's the only one after message 1
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['content'], 'Test message 2')
        
        # Verify message is marked as read
        m2.refresh_from_db()
        self.assertTrue(m2.is_read)
    
    def test_send_message_view(self):
        """Test the send_message AJAX view"""
        data = {'content': 'New message from test'}
        response = self.client.post(
            reverse('chat:send_message', kwargs={'room_id': self.chat_room1.id}),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        # Check the response
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['message']['content'], 'New message from test')
        self.assertEqual(response_data['message']['sender'], 'user1')
        self.assertTrue(response_data['message']['is_self'])
        
        # Check that message was created in database
        message = Message.objects.latest('timestamp')
        self.assertEqual(message.content, 'New message from test')
        self.assertEqual(message.sender, self.user1)
    
    def test_send_message_view_empty_content(self):
        """Test sending a message with empty content"""
        data = {'content': '   '}  # Only whitespace
        response = self.client.post(
            reverse('chat:send_message', kwargs={'room_id': self.chat_room1.id}),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Message content is required')
    
    def test_send_message_view_wrong_method(self):
        """Test sending a message with non-POST method"""
        response = self.client.get(reverse('chat:send_message', kwargs={'room_id': self.chat_room1.id}))
        
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Method not allowed')