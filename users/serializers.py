from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(style={'input_type':'password'},write_only=True, min_length=6, required=True)
    confirm_password = serializers.CharField(style={'input_type':'password'},write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "confirm_password"]

    def validate(self, data):
        
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm password must match password."})
        return data

    def create(self, validated_data):
        
        validated_data.pop("confirm_password")  
        user = User.objects.create_user(**validated_data)
        return user
    


class LoginSerializer(serializers.Serializer):
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        data["user"] = user
        return data
    
# for swagger documenation
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    

# for swagger documenation
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField()



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']



class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Just to include the username or user-related info
    profile_picture_url = serializers.SerializerMethodField()
    rank = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'profile_picture', 'profile_picture_url', 'points', 'rank', 'github', 'linkedin', 'twitter', 'facebook', 'full_name', 'location']

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture.url)
        return None

