from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .utils.gemini import generate_with_gemini
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class GeminiAssistantAPI(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get or Create Active Conversation",
        operation_description="Retrieves the user's active conversation or creates one if none exists.",
        responses={200: ConversationSerializer()}
    )

    def get(self, request):
        # Get or create active conversation
        conversation, created = Conversation.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={'is_active': True}
        )
        
        # If not newly created, deactivate all other conversations
        if not created:
            Conversation.objects.filter(user=request.user, is_active=True).exclude(id=conversation.id).update(is_active=False)
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Send Message to Gemini Assistant",
        operation_description="Sends a user message to the Gemini assistant and receives a generated response.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='User message to the assistant'),
                'max_tokens': openapi.Schema(type=openapi.TYPE_INTEGER, description='Maximum tokens for the model response', default=300),
            },
            required=['message']
        ),
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'response': openapi.Schema(type=openapi.TYPE_STRING, description='Assistant\'s reply'),
                'conversation_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the active conversation'),
            }
        )}
    )
    def post(self, request):
        user_message = request.data.get('message', '')
        max_tokens = request.data.get('max_tokens', 300)
        
        # Get active conversation or create new one
        conversation = Conversation.objects.filter(user=request.user, is_active=True).first()
        if not conversation:
            conversation = Conversation.objects.create(user=request.user, is_active=True)
        
       
        Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )
        
        # Get last 3 messages 
        last_messages = Message.objects.filter(
            conversation=conversation
        ).exclude(content=user_message).order_by('-created_at')[:3]
        
        
        chat_history = []
        for msg in reversed(last_messages):
            role = "user" if msg.is_user else "model"
            chat_history.append({
                "role": role,
                "parts": [msg.content]
            })
        
       
        bot_response = generate_with_gemini(
            prompt=user_message,
            max_tokens=max_tokens,
            chat_history=chat_history if chat_history else None
        )
        
        # Save bot response
        Message.objects.create(
            conversation=conversation,
            content=bot_response,
            is_user=False
        )
        
        return Response({
            'response': bot_response,
            'conversation_id': conversation.id
        })
class ResetConversationAPI(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Reset Conversation",
        operation_description="Deletes all active conversations and associated messages for the authenticated user.",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, example='success'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, example='Conversation and messages deleted successfully'),
            }
        )}
    )

    def post(self, request):
        
        conversations = Conversation.objects.filter(user=request.user, is_active=True)
        
        # First delete all messages in these conversations
        Message.objects.filter(conversation__in=conversations).delete()
        
        # Then delete the conversations 
        conversations.delete()
        
        return Response({
            'status': 'success',
            'message': 'Conversation and messages deleted successfully'
        }, status=status.HTTP_200_OK)