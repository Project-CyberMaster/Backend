from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

class CategoryListCreate(APIView):
    def get(self, request, format=None):
        name = request.query_params.get('name', None)  
        categories = Category.objects.all()

        if name:
            categories = categories.filter(name__icontains=name)  
            
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

class CategoryDetail(APIView):
    def get(self, request, pk, format=None):
        category = get_object_or_404(Category,pk=pk)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
