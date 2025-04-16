from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactSerializer
from drf_yasg.utils import swagger_auto_schema

class ContactAPIView(APIView):

    @swagger_auto_schema(
        request_body=ContactSerializer,
        operation_description="Send Message or Question For Help To The Staff Via Contact Form "
    )

    def post(self, request):
        
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Thank you for contacting us!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
