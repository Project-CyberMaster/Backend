from django.db import models

class Course(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()


class Lesson(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    course=models.ForeignKey(Course,related_name="lessons",on_delete=models.CASCADE)
    content=models.FileField(upload_to='lesson_content/', blank=True, null=True)
    order_index=models.IntegerField()

    class Meta:
        ordering = ["order_index"]
