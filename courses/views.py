from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *

class CourseList(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,format=None):
        course_list=Course.objects.all()
        serializer=CourseSerializer(course_list,many=True,context={'request':request})
        return Response(serializer.data)
    
class GetCourse(APIView):
    permission_classes=[IsAuthenticated]

    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise Http404
        
    def get(self,request,pk,format=None):
        course=self.get_object(pk)
        serializer=CourseSerializer(course,context={'request':request})
        return Response(serializer.data)
    
class LessonList(APIView):
    permission_classes=[IsAuthenticated]

    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise Http404
        
    def get(self,request,pk,format=None):
        course=self.get_object(pk)
        lessons=course.lessons.all()
        serializer=LessonSerializer(lessons,many=True,context={'request':request})
        return Response(serializer.data)
    
class GetLesson(APIView):
    permission_classes=[IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise Http404
        
    def get(self,request,pk,index,format=None):
        course=self.get_object(pk)
        try:
            lesson=course.lessons.get(order_index=index)
        except:
            raise Http404
        serializer=LessonSerializer(lesson,context={'request':request})
        return Response(serializer.data)
    
class Enroll(generics.CreateAPIView):
    serializer_class=EnrollmentsSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        course = get_object_or_404(Course,pk=self.kwargs['pk'])
        
        serializer.save(
            course = course,
            user=self.request.user
        )
        return super().perform_create(serializer)
    
class CompleteLesson(generics.UpdateAPIView):
    serializer_class=EnrollmentsSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        index = self.kwargs['index']
        course = get_object_or_404(Course,pk=self.kwargs['pk'])
        lesson = get_object_or_404(course.lessons.all(),order_index=index)
        lesson_count=course.lessons.count()

        serializer.instance.completed_lessons.add(lesson)

        serializer.instance.update_percentage()

        if index>=lesson_count:
            new_index=index
        else:
            new_index=index+1

        serializer.save(
            current_lesson_index=new_index
        )
