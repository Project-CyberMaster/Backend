from django.urls import path
from .views import *

urlpatterns=[
    path('courses',CourseList.as_view(),name='list-courses'),
    path('courses/<int:pk>',GetCourse.as_view(),name='list-courses'),
    path('courses/<int:pk>/lessons',LessonList.as_view(),name='list-courses'),
    path('courses/<int:pk>/lessons/<int:index>',GetLesson.as_view(),name='list-courses')
]