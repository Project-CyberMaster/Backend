from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    red_team_precent = models.PositiveIntegerField(default=0)
    blue_team_precent = models.PositiveIntegerField(default=0)
    objects=CustomUserManager()

    def __str__(self):
        return self.username