from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from django.contrib.auth import update_session_auth_hash
from rest_framework.exceptions import ValidationError
from django_rest_passwordreset.models import ResetPasswordToken
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        operation_description="Logout by blacklisting the refresh token."
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
   
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        operation_description="Logout by blacklisting the refresh token."
    )

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



class LogoutView(APIView):
    permissions_clases  = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        operation_description="Logout by blacklisting the refresh token."
    )

    
    def post(self, request):
       
        try:
            refresh_toke = request.data["refresh"]
            token = RefreshToken(refresh_toke)
            token.blacklist()


            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        operation_description="Verify OTP and reset the user's password. Requires email, OTP code, and new password."
    )

    def post(self, request):
        """Verify the otp and reset password by request an otp and submit it to change and password """
        email = request.data.get("email")
        otp_code = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp_code or not new_password:
            return Response(
                {"error": "Enter the email ,otp , and the new password"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

       
        

        # Check if OTP is valid
        reset_token = ResetPasswordToken.objects.filter(user__email=email, key=otp_code).first()
        if not reset_token:
            return Response(
                {"error": "OTP invalide or email incorrect."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset the password
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Delete the used OTP token
        reset_token.delete()

        return Response(
            {"message": "password reset sucssefully."}, 
            status=status.HTTP_200_OK
        )

    
class ProfileDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ProfileSerializer,
        operation_description="Logout by blacklisting the refresh token."
    )

    def get_object(self, user):
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return None

    def get(self, request, format=None):
        profile = self.get_object(request.user)
        if profile:
            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None):
        profile = self.get_object(request.user)
        if not profile:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = profile.user  # Get the associated user instance

        # Handle username, email, password, and profile data update
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if username:
            user.username = username
        
        if email:
            user.email = email

        if password:
            
            user.set_password(password)
        
        # Now update the profile fields if they are provided
        serializer = ProfileSerializer(profile, data=request.data, context={'request': request}, partial=True)

        if serializer.is_valid():
            
            user.save()
            # If password was changed, update the session authentication
            if password:
                update_session_auth_hash(request, user)  # Avoid logging out the user after password change
            serializer.save() 
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    

