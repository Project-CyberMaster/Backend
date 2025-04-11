from rest_framework import serializers
from .models import Category
from labs.serializers import LabSerializer
from courses.serializers import CourseSerializer

class CategorySerializer(serializers.ModelSerializer):
    labs = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'category_type', 'labs', 'courses']

    def get_labs(self,obj):
        request = self.context.get('request')
        expand = request.query_params.get('expand','').split(',')

        if 'labs' in expand:
            return LabSerializer(obj.labs.all(),many=True, read_only=True,context={'request':request}).data
        else:
            return list(obj.labs.values_list('id',flat=True))
        
    def get_courses(self,obj):
        request = self.context.get('request')
        expand = request.query_params.get('expand','').split(',')

        if 'courses' in expand:
            return CourseSerializer(obj.courses.all(),many=True, read_only=True,context={'request':request}).data
        else:
            return list(obj.courses.values_list('id',flat=True))
            