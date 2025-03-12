from django.db import models
from users.models import CustomUser

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
        unique_together = ("course","order_index")

class Enrollment(models.Model):
    course=models.ForeignKey(Course,related_name="students",on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,related_name="enrollments",on_delete=models.CASCADE)
    current_lesson_index=models.PositiveIntegerField(default=1)
    completed_lessons=models.ManyToManyField(Lesson,related_name='completed_lessons')
    completion_percentage=models.PositiveIntegerField(default=0)

    def update_percentage(self):
        lesson_count = self.course.lessons.count()
        completed_count = self.completed_lessons.count()
        
        if lesson_count > 0:
            self.completion_percentage = (completed_count/lesson_count)*100
        else:
            self.completion_percentage = 100
        
        self.save()

        return self.completion_percentage
    
    class Meta:
        unique_together = ('course','user')