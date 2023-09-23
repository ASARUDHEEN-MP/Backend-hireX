import json
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from User.models import CustomUser
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
       
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # add to database
    async def add_chat(self, data):

        sender = await self.get_user(data['from'])

        recipient = await self.get_user(data['to'])
        content = data['content']

        await sync_to_async(Message.objects.create)(sender=sender, recipient=recipient, content=content )

        print('message created')

    # Function to get the user asynchronously
    @database_sync_to_async
    def get_user(self, user_id):
        user=CustomUser.objects.get(id=user_id)
        return user

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json.get("event")
        if event == "chat":
             message = text_data_json["message"]
             print(message)
             to = text_data_json.get("to")
             frm = text_data_json.get("from")
             created_at = datetime.datetime.now().isoformat()
             data = {'from': frm, 'to': to, 'content': message}
             await self.add_chat(data)
             user_instance = await self.get_user(to)
             room_group_name = f"chat_{user_instance.id}"
             await self.channel_layer.group_send(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'event': 'chat_message',
                        'content': message,
                        'sender': frm,
                        'recipient': to,
                        'created_at': created_at,
                    }
                }
            )
        else:
            print('Only Chat features implemented')
            pass

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        print(f"Received message: {message}")
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
