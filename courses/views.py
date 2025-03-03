from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from .models import *
from .serializers import *

class CourseList(APIView):
    def get(self,request,format=None):
        course_list=Course.objects.all()
        serializer=CourseSerializer(course_list,many=True,context={'request':request})
        return Response(serializer.data)
    
class GetCourse(APIView):
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