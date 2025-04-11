from django.urls import path
from .views import  *

urlpatterns = [
    path('', LabListCreate.as_view(), name='lab-list-create'),
    path('<int:pk>', LabDetail.as_view(), name='lab-detail'),
    path('search', Search.as_view(), name='lab-search'),
   
    path('<int:lab_id>/files', LabResourceFileListCreate.as_view(), name='lab-file-list-create'),
    path('files/<int:pk>/', LabResourceFileDetail.as_view(), name='lab-file-detail'),
]