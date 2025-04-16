from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .utils.gemini import generate_with_gemini

User = get_user_model()

class GeminiAssistantAPI(APIView):
    permission_classes = [IsAuthenticated]
    
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