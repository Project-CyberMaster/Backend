from rest_framework import serializers
from .models import *

class LessonSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()
    markdown = serializers.SerializerMethodField()

    class Meta:
        model=Lesson
        fields=['id','title','description','chapter','link','markdown','order_index']

    def get_link(self,obj):
        if not obj.content:
            print('no content')
            return None
        try:
            obj.content.open(mode='r')
            lines = obj.content.readlines()
            obj.content.close()

            if lines and len(lines) > 0:
                return lines[0].strip()
            
            return None
        except Exception as e:
            return None
        
    def get_markdown(self,obj):
        if not obj.content:
            print('no content')
            return None
        try:
            obj.content.open(mode='r')
            lines = obj.content.readlines()
            obj.content.close()
            if lines and len(lines) > 0:
                return ''.join(lines[1:])
            
            return None
        except Exception as e:
            return None

class EnrollmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Enrollment
        fields=['course','user','current_lesson_index','completion_percentage']
        read_only_fields = ['course','user','current_lesson_index','completion_percentage']

class ChapterSerializer(serializers.ModelSerializer):
    lessons=LessonSerializer(many=True,read_only=True)
    class Meta:
        model=Chapter
        fields=['id','title','description','course','order_index','lessons']

class CourseSerializer(serializers.ModelSerializer):
    chapters=ChapterSerializer(many=True,read_only=True)
    class Meta:
        model=Course
        fields=['id','title','description','chapters']


