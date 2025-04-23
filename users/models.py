from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    red_team_percent = models.PositiveIntegerField(default=0)
    blue_team_percent = models.PositiveIntegerField(default=0)
    objects=CustomUserManager()

    def __str__(self):
        return self.username
    
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    points = models.IntegerField(default=0)
    rank = models.CharField(max_length=50, blank=True, null=True)

    full_name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)

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
        self.rank = self.calculate_rank() #update rank before saving
        super().save(*args, **kwargs)