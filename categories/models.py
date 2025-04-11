from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category_type = models.CharField(max_length=50, choices=[('offensive', 'Offensive'), ('defensive', 'Defensive'), ('both', 'Both')])

    def __str__(self):
        return self.name