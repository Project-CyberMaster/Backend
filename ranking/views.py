from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Profile
from users.serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class Leaderboard(APIView):
    @swagger_auto_schema(
        operation_summary="Leaderboard",
        operation_description="Get a list of user profiles ordered by points.",
        responses={200: ProfileSerializer(many=True)}
    )
    def get(self, request, format=None):
        profiles = Profile.objects.all().order_by('-points')  
        serializer = ProfileSerializer(profiles, many=True, context={'request': request})
        return Response(serializer.data)
