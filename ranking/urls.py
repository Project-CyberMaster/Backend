from django.urls import path
from .views import Leaderboard

urlpatterns = [
    path('leaderboard/', Leaderboard.as_view(), name='leaderboard'),
]