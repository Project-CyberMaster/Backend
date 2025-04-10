from rest_framework import serializers
from .models import *

class LessonSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()
    markdown = serializers.SerializerMethodField()

    class Meta:
        model=Lesson
        fields=['id','title','description','chapter','link','markdown','order_index']
    
    def get_fields(self):
        request=self.context.get('request')
        expand=request.query_params.get('expand','').split(',')
        fields=super().get_fields()

        if 'link' not in expand:
            del fields['link']

        if 'markdown' not in expand:
            del fields['markdown']      

        return fields

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
    lessons=serializers.SerializerMethodField()

    class Meta:
        model=Chapter
        fields=['id','title','description','course','order_index','lessons']

    def get_lessons(self,obj):
        request=self.context.get('request')
        expand=request.query_params.get('expand','').split(',')

        if 'lessons' in expand:
            return LessonSerializer(obj.lessons.all(),many=True,read_only=True,context={'request':request}).data
        
        return list(obj.lessons.values_list('id',flat=True))

class CourseSerializer(serializers.ModelSerializer):
    chapters=serializers.SerializerMethodField()
    thumbnail=serializers.SerializerMethodField()

    class Meta:
        model=Course
        fields=['id','title','description','thumbnail','chapters']

    def get_chapters(self,obj):
        request=self.context.get('request')
        expand=request.query_params.get('expand','').split(',')

        if 'chapters' in expand:
            return ChapterSerializer(obj.chapters.all(),many=True,read_only=True,context={'request':request}).data
        
        return list(obj.chapters.values_list('id',flat=True))
    
    def get_thumbnail(self,obj):
        if obj.thumbnail:
            return self.context['request'].build_absolute_uri(obj.thumbnail.url)

