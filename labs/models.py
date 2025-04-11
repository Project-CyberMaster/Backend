from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category_type = models.CharField(max_length=50, choices=[('offensive', 'Offensive'), ('defensive', 'Defensive'), ('both', 'Both')])

    def __str__(self):
        return self.name


class Lab(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    points = models.IntegerField()
    author = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='labs', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='labs', on_delete=models.CASCADE)

    connection_info = models.TextField(blank=True, null=True)  
    flag = models.CharField(max_length=255, blank=True, null=True) 
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='easy') 

    def __str__(self):
        return f"{self.title} ({self.difficulty})"


class LabResourceFile(models.Model):
    resource = models.ForeignKey(Lab, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='lab_resources/', blank=True, null=True)  
     

    def __str__(self):
        return self.file.name
