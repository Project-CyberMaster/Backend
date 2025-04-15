from django.urls import path
from .views import  *

urlpatterns = [
   
    path('categories/', CategoryList.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
   
    path('', LabList.as_view(), name='lab-list-create'),
    path('<int:pk>', LabDetail.as_view(), name='lab-detail'),
    path('search', Search.as_view(), name='lab-search'),
   
    path('<int:lab_id>/files', LabResourceFileList.as_view(), name='lab-file-list-create'),
    path('files/<int:pk>/', LabResourceFileDetail.as_view(), name='lab-file-detail'),
    path('progress/', SolveProgress.as_view(), name='solve-progress'),

]