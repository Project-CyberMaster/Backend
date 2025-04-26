from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CourseList(APIView):
    permission_classes=[IsAuthenticated]
    @swagger_auto_schema(
        operation_description="List all available courses",
        responses={200: CourseSerializer(many=True)}
    )

    def get(self,request):
        course_list=Course.objects.all()
        return Response(CourseSerializer(course_list,many=True,context={'request':request}).data)
    
class GetCourse(APIView):
    permission_classes=[IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Retrieve a single course by its ID",
        responses={200: CourseSerializer}
    )

    def get(self,request,pk):
        course=get_object_or_404(Course,pk=pk)
        serializer=CourseSerializer(course,context={'request':request})
        return Response(serializer.data)
    
class ChapterList(APIView):
    permission_classes=[IsAuthenticated]
    @swagger_auto_schema(
        operation_description="List all chapters for a given course",
        responses={200: ChapterSerializer(many=True)}
    )

    def get(self,request,pk):
        course=get_object_or_404(Course,pk=pk)
        chapters=course.chapters.all()
        return Response(ChapterSerializer(chapters,many=True,context={'request':request}).data)

class GetChapter(APIView):
    permission_classes=[IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Retrieve a specific chapter by course and chapter index",
        responses={200: ChapterSerializer}
    )

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
    @swagger_auto_schema(
        operation_description="List all lessons for a given chapter of a course",
        responses={200: LessonSerializer(many=True)}
    )

    def get(self,request,pk,index):
        course=get_object_or_404(Course,pk=pk)
        try:
            chapter=course.chapters.get(order_index=index)
        except:
            raise Http404
        lessons=chapter.lessons.all()
        return Response(LessonSerializer(lessons,many=True,context={'request':request}).data)
    
class GetLesson(APIView):
    permission_classes=[IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Retrieve a specific lesson by course, chapter index, and lesson index",
        responses={200: LessonSerializer}
    )

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
    @swagger_auto_schema(
        operation_description="Enroll in a course",
        request_body=EnrollmentsSerializer,
        responses={201: EnrollmentsSerializer}
    )

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
    @swagger_auto_schema(
        operation_description="Mark a lesson as completed and update progress",
        request_body=EnrollmentsSerializer,
        responses={200: EnrollmentsSerializer}
    )

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user,course__pk=self.kwargs['pk'])
    
    def get_object(self):
        queryset=self.get_queryset()
        return get_object_or_404(queryset)

    def perform_update(self, serializer):
        index = self.kwargs['index']
        lesson_index = self.kwargs['lessonindex']
        course = get_object_or_404(Course,pk=self.kwargs['pk'])
        chapter = get_object_or_404(course.chapters.all(),order_index=index)
        lesson = get_object_or_404(chapter.lessons.all(),order_index=lesson_index)
        lesson_count=chapter.lessons.count()

        if lesson in serializer.instance.completed_lessons.all():
            return
        
        serializer.instance.completed_lessons.add(lesson)

        serializer.instance.update_percentage()
        if serializer.instance.completion_percentage == 100.0:
            cert_ready=True
        else:
            cert_ready=False
        
        if lesson_index>=lesson_count:
            new_index=index
        else:
            new_index=index+1

        serializer.save(
            current_lesson_index=new_index,
            cert_ready=cert_ready
        )
    
class Search(APIView):
    @swagger_auto_schema(
        operation_description="Search courses, chapters, and lessons by query string",
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Search query",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: openapi.Response(
            description="Search results",
            examples={
                "application/json": {
                    "courses": [{"id": 1, "title": "Course 1", "description": "desc", "category": 1, "category__name": "Cat 1"}],
                    "chapters": [{"id": 1, "title": "Chapter 1", "description": "desc"}],
                    "lessons": [{"id": 1, "title": "Lesson 1", "description": "desc"}]
                }
            }
        )}
    )
    
    def get(self,request):
        query = request.GET.get('query',None)
        if not query:
            return Response({"error": "Query cannot be empty"}, status=400)
        
        course_results = Course.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query) ).values("id","title","description","category","category__name")
        chapter_results = Chapter.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) ).values("id","title","description")
        lesson_results = Lesson.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) ).values("id","title","description")
        
        return Response({
            "courses":course_results,
            "chapters":chapter_results,
            "lessons":lesson_results
        })