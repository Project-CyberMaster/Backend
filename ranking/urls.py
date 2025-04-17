from django.urls import path
from .views import Leaderboard

urlpatterns = [
    path('', Leaderboard.as_view(), name='leaderboard'),
]