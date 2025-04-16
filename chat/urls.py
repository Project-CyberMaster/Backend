from django.urls import path
from .views import GeminiAssistantAPI, ResetConversationAPI

urlpatterns = [
    path('', GeminiAssistantAPI.as_view(), name='assistant'),
    path('reset/', ResetConversationAPI.as_view(), name='reset-conversation'),
]