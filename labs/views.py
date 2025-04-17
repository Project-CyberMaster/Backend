from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .utils.percentage import calculate_solve_percentages
    
#lab views
class LabList(APIView):
    def get(self, request, format=None):
        difficulty = request.query_params.get('difficulty', None) 
        labs = Lab.objects.all()

        if difficulty:
            labs = labs.filter(difficulty=difficulty)  

        serializer = LabSerializer(labs, many=True, context={'request': request})
        return Response(serializer.data)

class LabDetail(APIView):
    def get(self, request, pk, format=None):
        lab = get_object_or_404(Lab,pk=pk)
        serializer = LabSerializer(lab, context={'request': request})
        return Response(serializer.data)

#labresources views
class LabResourceFileList(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def get(self, request, lab_id, format=None):
        lab_files = LabResourceFile.objects.filter(resource_id=lab_id)
        serializer = LabResourceFileSerializer(lab_files, many=True, context={'request': request})
        return Response(serializer.data)

class LabResourceFileDetail(APIView):
    def get(self, request, pk, format=None):
        lab_file = get_object_or_404(LabResourceFile,pk=pk)
        serializer = LabResourceFileSerializer(lab_file, context={'request': request})
        return Response(serializer.data)

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

            # Save solved lab
            SolvedLab.objects.get_or_create(user=request.user, lab=lab)

            return Response({"message": "Correct flag! Points added."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Incorrect flag!"}, status=status.HTTP_400_BAD_REQUEST)
        

class SolveProgress(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progress = calculate_solve_percentages(request.user)
        return Response(progress, status=200)


class Search(APIView):
    def get(self,request):
        query = request.GET.get('query',None)
        if not query:
            return Response({"error": "Query cannot be empty"}, status=400)
        
        results = Lab.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(author__icontains=query) | Q(category__name__icontains=query)).values("id","title","description","points","author","category__name")

        return Response(results)
    
