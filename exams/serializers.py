from rest_framework import serializers
from .models import *

class MCQChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQChoice
        fields = ['id', 'question', 'content', 'order_index']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['exam_attempt', 'question', 'submitted_answer', 'is_correct']

class ExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id', 'exam', 'user', 'score', 'started_at', 'duration', 'is_finished', 'cert_ready']

class QuestionSerializer(serializers.ModelSerializer):
    choices = MCQChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'exam', 'prompt', 'is_mcq', 'order_index', 'choices']
        # Don't expose correct_answer in the API for security

class ExamSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()
    user_has_passed = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ['id', 'title', 'course', 'duration', 'passing_score', 'questions_count', 'user_has_passed']
    
    def get_questions_count(self, obj):
        return obj.questions.count()
        
    def get_user_has_passed(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return ExamAttempt.objects.filter(
                user=request.user,
                exam=obj,
                cert_ready=True
            ).exists()
        return False