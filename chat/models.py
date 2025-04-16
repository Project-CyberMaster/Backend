from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField()  # True for user, False for bot
    created_at = models.DateTimeField(auto_now_add=True)