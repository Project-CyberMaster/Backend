from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
   
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Login successful",
                    "access": str(tokens.access_token),
                    "refresh": str(tokens),
                    
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileDetail(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get_object(self, user):
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, format=None):
        profile = self.get_object(request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def put(self, request, format=None):
        profile = self.get_object(request.user)
        serializer = ProfileSerializer(profile, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    

