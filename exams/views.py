from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
from django.utils import timezone as django_timezone
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class ExamList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context
    
class GetExam(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context
    
class QuestionList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        exam = get_object_or_404(Exam, pk=self.kwargs.get("pk"))
        
        # Check if user has an active exam attempt
        active_attempt = ExamAttempt.objects.filter(
            user=self.request.user,
            exam=exam,
            is_finished=False
        ).exists()
        
        if not active_attempt:
            return Question.objects.none()  # Return empty queryset if no active attempt
        
        return exam.questions.all().order_by('order_index')
    
    def list(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=self.kwargs.get("pk"))
        
        # Check for active attempt
        try:
            exam_attempt = get_object_or_404(
                ExamAttempt,
                user=request.user,
                exam=exam,
                is_finished=False
            )
            
            # Check if the exam attempt has timed out
            if exam_attempt.has_timed_out():
                # Automatically finish the exam
                now = django_timezone.now()
                duration = now - exam_attempt.started_at
                
                # Update exam attempt
                exam_attempt.is_finished = True
                exam_attempt.duration = duration
                exam_attempt.cert_ready = exam_attempt.score >= exam.passing_score
                exam_attempt.save()
                
                return Response({
                    'detail': 'Exam time limit exceeded. Your attempt has been automatically submitted.',
                    'final_score': exam_attempt.score,
                    'passed': exam_attempt.cert_ready
                }, status=status.HTTP_403_FORBIDDEN)
                
        except:
            return Response({
                "detail": "You must start the exam before accessing questions."
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                "detail": "You must start the exam before accessing questions."
            }, status=status.HTTP_403_FORBIDDEN)
            
        return super().list(request, *args, **kwargs)
    
class GetQuestion(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
    lookup_field = "order_index"

    def get_queryset(self):
        exam = get_object_or_404(Exam, pk=self.kwargs.get("pk"))
        
        # Check if user has an active exam attempt
        active_attempt = ExamAttempt.objects.filter(
            user=self.request.user,
            exam=exam,
            is_finished=False
        ).exists()
        
        if not active_attempt:
            return Question.objects.none()  # Return empty queryset if no active attempt
            
        return exam.questions.all()
        
    def retrieve(self, request, *args, **kwargs):
        try:
            # Get the exam
            exam = get_object_or_404(Exam, pk=self.kwargs.get("pk"))
            
            # Get the active attempt
            exam_attempt = get_object_or_404(
                ExamAttempt,
                user=request.user,
                exam=exam,
                is_finished=False
            )
            
            # Check if the exam attempt has timed out
            if exam_attempt.has_timed_out():
                # Automatically finish the exam
                now = django_timezone.now()
                duration = now - exam_attempt.started_at
                
                # Update exam attempt
                exam_attempt.is_finished = True
                exam_attempt.duration = duration
                exam_attempt.cert_ready = exam_attempt.score >= exam.passing_score
                exam_attempt.save()
                
                return Response({
                    'detail': 'Exam time limit exceeded. Your attempt has been automatically submitted.',
                    'final_score': exam_attempt.score,
                    'passed': exam_attempt.cert_ready
                }, status=status.HTTP_403_FORBIDDEN)
                
            instance = self.get_object()
            return super().retrieve(request, *args, **kwargs)
        except:
            return Response({
                "detail": "You must start the exam before accessing questions."
            }, status=status.HTTP_403_FORBIDDEN)

class StartExam(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        
        # Check if user has already passed this exam
        already_passed = ExamAttempt.objects.filter(
            user=request.user,
            exam=exam,
            cert_ready=True
        ).exists()
        
        if already_passed:
            return Response({
                'detail': 'You have already passed this exam and cannot make new attempts.',
                'cert_ready': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for unfinished attempts
        exam_attempt = ExamAttempt.objects.filter(
            user=request.user, 
            exam=exam, 
            is_finished=False
        ).first()
        
        if exam_attempt:
            # Check if the exam attempt has timed out
            if exam_attempt.has_timed_out():
                # Automatically finish the exam
                now = django_timezone.now()
                duration = now - exam_attempt.started_at
                
                # Update exam attempt
                exam_attempt.is_finished = True
                exam_attempt.duration = duration
                exam_attempt.cert_ready = exam_attempt.score >= exam.passing_score
                exam_attempt.save()
                
                # Create new attempt after the timed-out one is closed
                new_attempt = ExamAttempt.objects.create(
                    user=request.user,
                    exam=exam,
                    score=0,
                    is_finished=False,
                    cert_ready=False
                )
                
                serializer = ExamAttemptSerializer(new_attempt)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'detail': 'An unfinished exam attempt already exists',
                    'attempt_id': exam_attempt.id
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new attempt
        exam_attempt = ExamAttempt.objects.create(
            user=request.user,
            exam=exam,
            score=0,
            is_finished=False,
            cert_ready=False
        )
        
        serializer = ExamAttemptSerializer(exam_attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubmitAnswer(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        
        # Validate request data
        if 'question_id' not in request.data:
            return Response({'detail': 'question_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'answer' not in request.data:
            return Response({'detail': 'answer is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get current exam attempt
        exam_attempt = get_object_or_404(
            ExamAttempt, 
            user=request.user, 
            exam=exam, 
            is_finished=False
        )
        
        # Check if the exam attempt has timed out
        if exam_attempt.has_timed_out():
            # Automatically finish the exam
            now = django_timezone.now()
            duration = now - exam_attempt.started_at
            
            # Update exam attempt
            exam_attempt.is_finished = True
            exam_attempt.duration = duration
            exam_attempt.cert_ready = exam_attempt.score >= exam.passing_score
            exam_attempt.save()
            
            return Response({
                'detail': 'Exam time limit exceeded. Your attempt has been automatically submitted.',
                'final_score': exam_attempt.score,
                'passed': exam_attempt.cert_ready
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get question
        question_id = request.data.get('question_id')
        question = get_object_or_404(Question, id=question_id, exam=exam)
        
        # Check if question has already been answered
        existing_answer = Answer.objects.filter(
            exam_attempt=exam_attempt,
            question=question
        ).first()
        
        if existing_answer:
            return Response({
                'detail': 'This question has already been answered.',
                'is_correct': existing_answer.is_correct,
                'current_score': exam_attempt.score
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check answer
        is_correct = False
        user_answer = request.data.get('answer')
        
        if question.is_mcq:
            # For MCQ, answer should be the choice id
            try:
                selected_choice = MCQChoice.objects.get(id=user_answer, question=question)
                is_correct = selected_choice.is_correct
                # Store the choice ID as the submitted answer
                submitted_answer = str(selected_choice.id)
            except MCQChoice.DoesNotExist:
                return Response({'detail': 'Invalid choice'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # For text answers, compare with correct_answer
            is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()
            submitted_answer = user_answer
        
        # Create answer (no update since we're preventing re-answers)
        answer = Answer.objects.create(
            exam_attempt=exam_attempt,
            question=question,
            submitted_answer=submitted_answer,
            is_correct=is_correct
        )
        
        # Update score
        # Calculate total score based on all correct answers
        correct_answers = Answer.objects.filter(exam_attempt=exam_attempt, is_correct=True).count()
        total_questions = Question.objects.filter(exam=exam).count()
        
        if total_questions > 0:  # Avoid division by zero
            new_score = (correct_answers / total_questions) * 100
            exam_attempt.score = new_score
            exam_attempt.save()
        
        return Response({
            'is_correct': is_correct,
            'current_score': exam_attempt.score
        }, status=status.HTTP_200_OK)
       
class FinishExam(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        exam_attempt = get_object_or_404(
            ExamAttempt, 
            user=request.user, 
            exam=exam, 
            is_finished=False
        )
        
        # Calculate duration
        now = django_timezone.now()
        duration = now - exam_attempt.started_at
        
        # Determine if passed
        passed = exam_attempt.score >= exam.passing_score
        
        # Update exam attempt
        exam_attempt.is_finished = True
        exam_attempt.duration = duration
        exam_attempt.cert_ready = passed
        
        try:
            exam_attempt.save()
        except IntegrityError:
            # This would only happen if someone else marked a passing attempt
            # in the time between our check and save (highly unlikely)
            return Response({
                'detail': 'Another passing attempt was recorded. This attempt cannot be saved.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Return results
        serializer = ExamAttemptSerializer(exam_attempt)
        data = serializer.data
        data['passed'] = passed
        
        return Response(data, status=status.HTTP_200_OK)