from django.db import models
from courses.models import Course
from users.models import CustomUser

class Exam(models.Model):
    title=models.CharField(max_length=255)
    course=models.OneToOneField(Course,related_name='exams',on_delete=models.CASCADE)
    duration=models.DurationField()
    passing_score=models.IntegerField(default=50)

    def __str__(self):
        return self.title
    
class Question(models.Model):
    exam=models.ForeignKey(Exam,related_name="questions",on_delete=models.CASCADE)
    prompt=models.CharField(max_length=255)
    is_mcq=models.BooleanField(default=True)
    correct_answer=models.CharField(max_length=255,blank=True,null=True)
    order_index=models.IntegerField()

    def __str__(self):
        return self.prompt
    
class MCQChoice(models.Model):
    question=models.ForeignKey(Question,related_name="choices",on_delete=models.CASCADE)
    content=models.CharField(max_length=255)
    is_correct=models.BooleanField(default=False)
    order_index=models.IntegerField()

    def __str__(self):
        return self.content
    
class ExamAttempt(models.Model):
    exam=models.ForeignKey(Exam,related_name="runs",on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,related_name="exam_runs",on_delete=models.CASCADE)
    score=models.IntegerField(default=0)
    started_at=models.DateTimeField(auto_now_add=True)
    is_finished=models.BooleanField(default=False)
    duration=models.DurationField(blank=True,null=True)

    # def __str__(self):
    #     return self.title