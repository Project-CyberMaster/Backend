from django.urls import path
from .views import  *

urlpatterns = [
    path('', LabList.as_view(), name='lab-list-create'),
    path('<int:pk>', LabDetail.as_view(), name='lab-detail'),
    path('search', Search.as_view(), name='lab-search'),
   
    path('<int:lab_id>/files', LabResourceFileList.as_view(), name='lab-file-list-create'),
    path('files/<int:pk>/', LabResourceFileDetail.as_view(), name='lab-file-detail'),
    path('progress/', SolveProgress.as_view(), name='solve-progress'),
    path('submit_flag/<int:lab_id>/', SubmitFlag.as_view(), name='submit-flag'),
    path('badges/', BadgeList.as_view(), name='badge-list'),
    path('solved_labs/', SolvedLabList.as_view(), name='solved-lab-list'),

]