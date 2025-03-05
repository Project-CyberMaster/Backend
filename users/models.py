from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.contrib.auth import get_user_model



class CustomUser(AbstractUser):
    red_team_precent = models.PositiveIntegerField(default=0)
    blue_team_precent = models.PositiveIntegerField(default=0)
    objects=CustomUserManager()

    def __str__(self):
        return self.username
    
from django.contrib.auth import get_user_model 

User = get_user_model()
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    points = models.IntegerField(default=0)  # To track user points (for ranking later)
    rank = models.CharField(max_length=50, blank=True, null=True)  # To store user rank (for ranking later)

    def __str__(self):
        return f"{self.user.username}'s Profile"    
    
    def calculate_rank(self):
        if self.points >= 1001:
            return "Expert"
        elif self.points >= 501:
            return "Advanced"
        elif self.points >= 101:
            return "Intermediate"
        else:
            return "Beginner"

    def save(self, *args, **kwargs):
        self.rank = self.calculate_rank()  # Update rank before saving
        super().save(*args, **kwargs)