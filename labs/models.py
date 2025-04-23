from django.db import models
from categories.models import Category
from courses.models import Lesson
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Lab(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    is_machine=models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    points = models.IntegerField()
    author = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='labs', on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    lesson = models.ForeignKey(Lesson, related_name='labs', on_delete=models.CASCADE,)
    connection_info = models.TextField(blank=True, null=True)  
    flag = models.CharField(max_length=255, blank=True, null=True) 
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='easy') 

    def __str__(self):
        return f"{self.title} ({self.difficulty})"

class LabResourceFile(models.Model):
    resource = models.ForeignKey(Lab, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='lab_resources/', blank=True, null=True)  
     

    def __str__(self):
     if self.file:
        return f"Resource File: {self.file.name}"
     return "Resource File: [No file uploaded]"

class SolvedLab(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    solved_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lab')  # avoid duplicates

    def __str__(self):
        return f"{self.user.username} - {self.lab.title}"

class Badge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge_name = models.CharField(max_length=100)
    earned_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.badge_name} Earned By {self.user.username} on {self.earned_on}"