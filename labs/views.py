from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

#categorie views

class CategoryListCreate(APIView):
    def get(self, request, format=None):
        name = request.query_params.get('name', None)  
        categories = Category.objects.all()

        if name:
            categories = categories.filter(name__icontains=name)  
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

#lab views
    


class LabListCreate(APIView):
    def get(self, request, format=None):
        difficulty = request.query_params.get('difficulty', None) 
        labs = Lab.objects.all()

        if difficulty:
            labs = labs.filter(difficulty=difficulty)  

        serializer = LabSerializer(labs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = LabSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LabDetail(APIView):
    def get_object(self, pk):
        try:
            return Lab.objects.get(pk=pk)
        except Lab.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk, format=None):
        lab = self.get_object(pk)
        serializer = LabSerializer(lab, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        lab = self.get_object(pk)
        serializer = LabSerializer(lab, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        lab = self.get_object(pk)
        lab.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

#labresources views



class LabResourceFileListCreate(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def get(self, request, lab_id, format=None):
        lab_files = LabResourceFile.objects.filter(resource_id=lab_id)
        serializer = LabResourceFileSerializer(lab_files, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, lab_id, format=None):
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        lab_file = LabResourceFile.objects.create(resource=lab, file=file)
        serializer = LabResourceFileSerializer(lab_file, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LabResourceFileDetail(APIView):
    def get_object(self, pk):
        try:
            return LabResourceFile.objects.get(pk=pk)
        except LabResourceFile.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk, format=None):
        lab_file = self.get_object(pk)
        serializer = LabResourceFileSerializer(lab_file, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        lab_file = self.get_object(pk)
        serializer = LabResourceFileSerializer(lab_file, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        lab_file = self.get_object(pk)
        lab_file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class SubmitFlag(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, lab_id, format=None):
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            return Response({"error": "Lab not found"}, status=status.HTTP_404_NOT_FOUND)

        user_flag = request.data.get('flag', '')
        if user_flag == lab.flag:
            # Update user's points
            profile = request.user.profile
            profile.points += lab.points
            profile.save()

            return Response({"message": "Correct flag! Points added."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Incorrect flag!"}, status=status.HTTP_400_BAD_REQUEST)
