from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *

class CourseList(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        course_list=Course.objects.values("id","title","description")
        return Response(list(course_list))
    
class GetCourse(APIView):
    permission_classes=[IsAuthenticated]
        
    def get(self,request,pk):
        course=get_object_or_404(Course,pk=pk)
        serializer=CourseSerializer(course,context={'request':request})
        return Response(serializer.data)
    
class ChapterList(APIView):
    permission_classes=[IsAuthenticated]
        
    def get(self,request,pk):
        course=get_object_or_404(Course,pk=pk)
        chapters=course.chapters.values("id","title","description")
        return Response(list(chapters))

class GetChapter(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,pk,index):
        course=get_object_or_404(Course,pk=pk)
        try:
            chapter=course.chapters.get(order_index=index)
        except:
            raise Http404
        serializer=ChapterSerializer(chapter,context={'request':request})
        return Response(serializer.data)
    
class LessonList(APIView):
    permission_classes=[IsAuthenticated]
        
    def get(self,request,pk,index):
        course=get_object_or_404(Course,pk=pk)
        try:
            chapter=course.chapters.get(order_index=index)
        except:
            raise Http404
        lessons=chapter.lessons.values("id","title","description")
        return Response(list(lessons))
    
class GetLesson(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,pk,index,lessonindex):
        course=get_object_or_404(Course,pk=pk)
        try:
            chapter=course.chapters.get(order_index=index)
        except:
            raise Http404
        
        try:
            lesson=chapter.lessons.get(order_index=lessonindex)
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
        lesson_index = self.kwargs['lesson_index']
        course = get_object_or_404(Course,pk=self.kwargs['pk'])
        chapter = get_object_or_404(course.chapters.all(),order_index=index)
        lesson = get_object_or_404(chapter.lessons.all(),order_index=lesson_index)
        lesson_count=chapter.lessons.count()

        serializer.instance.completed_lessons.add(lesson)

        serializer.instance.update_percentage()

        if index>=lesson_count:
            new_index=index
        else:
            new_index=index+1

        serializer.save(
            current_lesson_index=new_index
        )

class Search(APIView):
    def get(self,request):
        query = request.GET.get('query',None)
        if not query:
            return Response({"error": "Query cannot be empty"}, status=400)
        
        course_results = Course.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) ).values("id","title","description")
        chapter_results = Chapter.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) ).values("id","title","description")
        lesson_results = Lesson.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) ).values("id","title","description")
        
        return Response({
            "courses":course_results,
            "chapters":chapter_results,
            "lessons":lesson_results
        })