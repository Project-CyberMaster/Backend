from django.urls import path
from .views import *

urlpatterns=[
    path('',CourseList.as_view(),name='list-courses'),
    path('<int:pk>',GetCourse.as_view(),name='get-course'),
    path('<int:pk>/lessons',LessonList.as_view(),name='list-lessons'),
    path('<int:pk>/lessons/<int:index>',GetLesson.as_view(),name='get-lesson'),
    path('<int:pk>/lessons/<int:index>/complete',CompleteLesson.as_view(),name='complete-lesson'),
    path('<int:pk>/enroll',Enroll.as_view(),name='enroll'),
]