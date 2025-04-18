import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from student.models import Student, ExamNotification
from teacher.models import Teacher

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        # Create a user-specific group
        if self.user.is_authenticated:
            self.room_group_name = f'user_{self.user.id}'
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Join the broadcast group for all users
            await self.channel_layer.group_add(
                'broadcast',
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave room groups
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        await self.channel_layer.group_discard(
            'broadcast',
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'notification_read':
            notification_id = data.get('notification_id')
            await self.mark_notification_read(notification_id)
    
    # Mark notification as read
    @sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = ExamNotification.objects.get(id=notification_id)
            if notification.student.user == self.user:
                notification.is_read = True
                notification.save()
        except ExamNotification.DoesNotExist:
            pass
    
    # Receive message from room group
    async def notification_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
    
    # Receive broadcast message
    async def broadcast_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))


class SyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        # Only allow authenticated users
        if self.user.is_authenticated:
            # Join the sync group
            self.room_group_name = 'sync'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Handle different sync messages
        if message_type == 'exam_created':
            # Forward the message to the sync group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'sync_message',
                    'message': data
                }
            )
        elif message_type == 'result_submitted':
            # Forward the message to the sync group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'sync_message',
                    'message': data
                }
            )
    
    # Receive message from room group
    async def sync_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
