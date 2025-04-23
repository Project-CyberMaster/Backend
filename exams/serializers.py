from rest_framework import serializers
from .models import *

class MCQChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=MCQChoice
        fields=['question','content','order_index']

class ExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model=ExamAttempt
        fields=['exam','user','score','started_at','duration']

class QuestionSerializer(serializers.ModelSerializer):
    choices=MCQChoiceSerializer(many=True)
    class Meta:
        model=Question
        fields=['exam','prompt','is_mcq','correct_answer','choices','order_index']

class ExamSerializer(serializers.ModelSerializer):
    questions=QuestionSerializer(many=True)
    class Meta:
        model=Exam
        fields=['title','course','duration','passing_score','questions']

