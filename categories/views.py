from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CategoryListCreate(APIView):
    @swagger_auto_schema(
        operation_description="List Categories",
        manual_parameters=[
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Filter categories by name (optional)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: CategorySerializer(many=True)}
    )

    def get(self, request, format=None):
        name = request.query_params.get('name', None)  
        categories = Category.objects.all()

        if name:
            categories = categories.filter(name__icontains=name)  
            
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

class CategoryDetail(APIView):
    @swagger_auto_schema(
        operation_description="View Category Details",
        responses={200: CategorySerializer}
    )
    
    def get(self, request, pk, format=None):
        category = get_object_or_404(Category,pk=pk)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
