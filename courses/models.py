from django.db import models
from users.models import CustomUser

class Course(models.Model):
    title=models.CharField(max_length=255)
    thumbnail=models.FileField(upload_to='thumbnails/', blank=True, null=True)
    description=models.TextField()

class Chapter(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    course=models.ForeignKey(Course,related_name="chapters",on_delete=models.CASCADE)
    order_index=models.IntegerField()

    class Meta:
        ordering = ["order_index"]
        unique_together = ("course","order_index")

class Lesson(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    chapter=models.ForeignKey(Chapter,related_name="lessons",on_delete=models.CASCADE)
    content=models.FileField(upload_to='lesson_content/', blank=True, null=True)
    order_index=models.IntegerField()

    class Meta:
        ordering = ["order_index"]
        unique_together = ("chapter","order_index")

class Enrollment(models.Model):
    course=models.ForeignKey(Course,related_name="students",on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,related_name="enrollments",on_delete=models.CASCADE)
    current_lesson_index=models.PositiveIntegerField(default=1)
    completed_lessons=models.ManyToManyField(Lesson,related_name='completed_lessons')
    completion_percentage=models.PositiveIntegerField(default=0)

    def update_percentage(self):
        lesson_count = Lesson.objects.filter(chapter__course=self.course).count()
        completed_count = self.completed_lessons.count()
        
        if lesson_count > 0:
            self.completion_percentage = (completed_count/lesson_count)*100
        else:
            self.completion_percentage = 100
        
        self.save()

        return self.completion_percentage
    
    class Meta:
        unique_together = ('course','user')