from django.urls import path
from .views import  (
    CategoryListCreate, CategoryDetail,
    LabListCreate, LabDetail,
    LabResourceFileListCreate, LabResourceFileDetail
)

urlpatterns = [
   
    path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),

   
    path('labs/', LabListCreate.as_view(), name='lab-list-create'),
    path('labs/<int:pk>/', LabDetail.as_view(), name='lab-detail'),

   
    path('labs/<int:lab_id>/files/', LabResourceFileListCreate.as_view(), name='lab-file-list-create'),
    path('files/<int:pk>/', LabResourceFileDetail.as_view(), name='lab-file-detail'),
]