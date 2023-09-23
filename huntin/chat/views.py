from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from chat.models import Message
from django.db.models import Q
from .Serializers import MessageSerializer
from User.models import UserImage,CustomUser
from django.http import JsonResponse

class ChatMessageApiView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, pk, company_id):
        try:
            messages = Message.objects.filter(
                (Q(sender=company_id) & Q(recipient=pk)) | (Q(sender=pk) & Q(recipient=company_id))
            ).order_by('-created_at')

            serializer = MessageSerializer(messages, many=True)
            return Response({
                'payload': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Chatviewall(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # Fetch messages where the user is either the sender or recipient
            messages = Message.objects.filter(
                Q(sender=pk) | Q(recipient=pk)
            )

            # Serialize the messages
            serializer = MessageSerializer(messages, many=True)

            # Get unique user IDs from sender and recipient fields
            sender_ids = list(messages.values_list('sender', flat=True))
            recipient_ids = list(messages.values_list('recipient', flat=True))
            user_ids = list(set(sender_ids + recipient_ids))

            # Get image URLs and usernames for the users
            user_data = {}
            users_added = set()  # Maintain a set of users already added to messages_data

            for user_id in user_ids:
                # Check if the user ID is the same as pk and skip it
                if user_id == pk:
                    continue

                # Check if the user ID is already added
                if user_id in users_added:
                    continue  # Skip adding duplicate user data

                # Retrieve recipient's image_url from UserImage model
                user_image = UserImage.objects.filter(user_id=user_id).first()
                if user_image:
                    image_url = user_image.image_url
                else:
                    image_url = None

                # Retrieve recipient's username from CustomUser model
                user = CustomUser.objects.get(id=user_id)
                username = user.username

                # Add user data to the dictionary and set
                user_data[user_id] = {
                    "id": user_id,
                    "image_url": image_url,
                    "username": username,
                }
                users_added.add(user_id)  # Add user to the set

            # Create a list of unique user data
            unique_user_data = list(user_data.values())

            # Create a list of message data with sender and recipient info
            messages_data = []
            for message in serializer.data:
                sender_info = user_data.get(message['sender'])
                recipient_info = user_data.get(message['recipient'])

                # Include sender and recipient data in the message
                message_data = {
                    "id": message['id'],
                    "content": message['content'],
                    "created_at": message['created_at'],
                    "sender_info": sender_info,
                    "recipient_info": recipient_info,
                }
                messages_data.append(message_data)

            response_data = {
                "users": unique_user_data,
            }
            print(response_data)
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Message.DoesNotExist:
            return JsonResponse(
                {"message": "Messages not found for the specified user."},
                status=status.HTTP_404_NOT_FOUND)


