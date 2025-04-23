from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class ExamList(generics.ListAPIView):
    # permission_classes=[IsAuthenticated]
    queryset=Exam.objects.all()
    serializer_class=ExamSerializer
    
class GetExam(generics.RetrieveAPIView):
    # permission_classes=[IsAuthenticated]
    queryset=Exam.objects.all()
    serializer_class=ExamSerializer
    
class QuestionList(generics.ListAPIView):
    # permission_classes=[IsAuthenticated]
    serializer_class=QuestionSerializer

    def get_queryset(self):
        return get_object_or_404(Exam,pk=self.kwargs.get("pk")).questions.all()
    
class GetQuestion(generics.RetrieveAPIView):
    # permission_classes=[IsAuthenticated]
    serializer_class=QuestionSerializer
    lookup_field="order_index"

    def get_queryset(self):
        exam=get_object_or_404(Exam,pk=self.kwargs.get("pk"))
        return exam.questions.all()

class StartExam(APIView):
    def post(self,request,pk):
        exam=get_object_or_404(Exam,pk=pk)
        exam_attempt=ExamAttempt.objects.filter(user=self.request.user,exam=exam).first()
        
        if exam_attempt:
            if not exam_attempt.is_finished:
                raise ValidationError({'details':'an unfinished exam attempt already exists'})
            
            serializer=ExamAttemptSerializer(
                exam_attempt,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save(is_finished=False,duration=0,started_at=datetime.datetime.now(datetime.timezone.uct))
                return Response(serializer.data,status=status.HTTP_200_OK)
        

        serializer=ExamAttemptSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(
                user=request.user,
                exam=exam
            )
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class SubmitAnswer(generics.CreateAPIView):
    pass
   
class FinishExam(generics.UpdateAPIView):
    pass