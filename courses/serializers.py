from rest_framework import serializers
from .models import Course,Lesson

class LessonSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()
    markdown = serializers.SerializerMethodField()

    class Meta:
        model=Lesson
        fields=['id','title','description','course','link','markdown','order_index']

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

class CourseSerializer(serializers.ModelSerializer):
    lessons=LessonSerializer(many=True,read_only=True)
    class Meta:
        model=Course
        fields=['id','title','description','lessons']
