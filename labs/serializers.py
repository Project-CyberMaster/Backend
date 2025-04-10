from rest_framework import serializers
from .models import Category, Lab, LabResourceFile

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
            'id', 'title', 'description', 'points', 'author', 'category', 'category_name',
            'connection_info', 'difficulty', 'files'
        ]

    def get_files(self,obj):
        request=self.context.get('request')
        expand=request.query_params.get('expand','').split(',')

        if 'files' in expand:
            return LabResourceFileSerializer(obj.files.all(),many=True,context={'request':request}).data
        
        return list(obj.files.values_list('id',flat=True))

class CategorySerializer(serializers.ModelSerializer):
    labs = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'category_type', 'labs']

    def get_labs(self,obj):
        request = self.context.get('request')
        expand = request.query_params.get('expand','').split(',')

        if 'labs' in expand:
            return LabSerializer(obj.labs.all(),many=True, read_only=True,context={'request':request}).data
        else:
            return list(obj.labs.values_list('id',flat=True))
