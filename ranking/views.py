from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Profile
from users.serializers import *

class Leaderboard(APIView):
    def get(self, request, format=None):
        profiles = Profile.objects.all().order_by('-points')  
        serializer = ProfileSerializer(profiles, many=True, context={'request': request})
        return Response(serializer.data)
