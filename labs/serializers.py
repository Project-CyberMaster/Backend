from rest_framework import serializers
from .models import *

class LabResourceFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()  

    class Meta:
        model = LabResourceFile
        fields = ['id', 'file', 'file_url']

    def get_file_url(self, obj):
        if obj.file:
            return self.context['request'].build_absolute_uri(obj.file.url)
        return None

class LabSerializer(serializers.ModelSerializer):
    # files = LabResourceFileSerializer(many=True, read_only=True)  
    files = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)  

    class Meta:
        model = Lab
        fields = [
            'id', 'is_machine','title', 'description', 'points','lesson', 'author', 'category', 'category_name',
            'connection_info', 'difficulty', 'files'
        ]

    def get_files(self,obj):
        request=self.context.get('request')
        expand=request.query_params.get('expand','').split(',')

        if 'files' in expand:
            return LabResourceFileSerializer(obj.files.all(),many=True,context={'request':request}).data
        
        return list(obj.files.values_list('id',flat=True))

class SolvedLabSerializer(serializers.ModelSerializer):
    lab_title = serializers.CharField(source='lab.title', read_only=True)
    solved_on = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SolvedLab
        fields = ['id', 'user', 'lab_title', 'solved_on']

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'user', 'badge_name', 'earned_on']