from django.db import models
from courses.models import Course
from users.models import CustomUser
from datetime import timedelta
from django.utils import timezone

class Exam(models.Model):
    title = models.CharField(max_length=255)
    course = models.OneToOneField(Course, related_name='exams', on_delete=models.CASCADE)
    duration = models.DurationField(help_text="Format: HH:MM:SS (e.g., 01:30:00 for 1 hour and 30 minutes)")
    passing_score = models.IntegerField(default=50)

    def __str__(self):
        return self.title
    
    @staticmethod
    def parse_duration(duration_str):
        """
        Helper method to parse duration string into timedelta
        Usage: duration = Exam.parse_duration("01:30:00")
        """
        if not duration_str:
            return None
            
        try:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                return timedelta(minutes=minutes, seconds=seconds)
            else:
                seconds = int(parts[0])
                return timedelta(seconds=seconds)
        except (ValueError, TypeError):
            return None
    
class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE)
    prompt = models.CharField(max_length=255)
    is_mcq = models.BooleanField(default=True)
    correct_answer = models.CharField(max_length=255, blank=True, null=True)
    order_index = models.IntegerField()

    def __str__(self):
        return self.prompt
    
class MCQChoice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order_index = models.IntegerField()

    def __str__(self):
        return self.content
    
class ExamAttempt(models.Model):
    exam = models.ForeignKey(Exam, related_name="runs", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name="exam_runs", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    duration = models.DurationField(blank=True, null=True)
    cert_ready = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"
    
    def has_timed_out(self):
        """Check if the exam attempt has exceeded the allowed duration"""
        if not self.exam.duration:
            return False
            
        now = timezone.now()
        elapsed_time = now - self.started_at
        return elapsed_time > self.exam.duration
        
    class Meta:
        # Add unique constraint to ensure one passing attempt per user per exam
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'exam', 'cert_ready'],
                condition=models.Q(cert_ready=True),
                name='unique_passing_attempt'
            )
        ]

class Answer(models.Model):
    exam_attempt = models.ForeignKey(ExamAttempt, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="student_answers", on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Answer to {self.question.prompt[:20]}..."