from django.urls import path
from .views import *

urlpatterns=[
    path('',CourseList.as_view(),name='list-courses'),
    path('<int:pk>',GetCourse.as_view(),name='list-courses'),
    path('<int:pk>/lessons',LessonList.as_view(),name='list-courses'),
    path('<int:pk>/lessons/<int:index>',GetLesson.as_view(),name='list-courses'),
]