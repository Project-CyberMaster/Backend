from django.db import models
from users.models import CustomUser
from categories.models import Category

class Course(models.Model):
    title=models.CharField(max_length=255)
    thumbnail=models.FileField(upload_to='thumbnails/', blank=True, null=True)
    description=models.TextField()
    category=models.ForeignKey(Category,related_name='courses',on_delete=models.CASCADE)
    author=models.CharField(max_length=255,default="")
    author_photo=models.FileField(upload_to='authors/', blank=True, null=True)
    author_role=models.CharField(max_length=255,default="")

    def __str__(self):
        return self.title
    
class Chapter(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    course=models.ForeignKey(Course,related_name="chapters",on_delete=models.CASCADE)
    order_index=models.IntegerField()

    class Meta:
        ordering = ["order_index"]
        unique_together = ("course","order_index")

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    chapter=models.ForeignKey(Chapter,related_name="lessons",on_delete=models.CASCADE)
    url=models.CharField(max_length=255,null=True)
    content=models.FileField(upload_to='lesson_content/', blank=True, null=True)
    order_index=models.IntegerField()

    class Meta:
        ordering = ["order_index"]
        unique_together = ("chapter","order_index")

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    course=models.ForeignKey(Course,related_name="students",on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,related_name="enrollments",on_delete=models.CASCADE)
    current_lesson_index=models.PositiveIntegerField(default=1)
    completed_lessons=models.ManyToManyField(Lesson,related_name='completed_lessons')
    completion_percentage=models.PositiveIntegerField(default=0)
    cert_ready=models.BooleanField(default=False)

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