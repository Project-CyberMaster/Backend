from django.urls import path
from .views import *

urlpatterns=[
    path('',CourseList.as_view(),name='list-courses'),
    path('<int:pk>',GetCourse.as_view(),name='get-course'),
    path('<int:pk>/chapters',ChapterList.as_view(),name='list-chapters'),
    path('<int:pk>/chapters/<int:index>',GetChapter.as_view(),name='get-chapter'),
    path('<int:pk>/chapters/<int:index>/lessons',LessonList.as_view(),name='list-lessons'),
    path('<int:pk>/chapters/<int:index>/lessons/<int:lessonindex>',GetLesson.as_view(),name='get-lesson'),
    path('<int:pk>/chapters/<int:index>/lessons/<int:lessonindex>/complete',CompleteLesson.as_view(),name='complete-lesson'),
    path('<int:pk>/enroll',Enroll.as_view(),name='enroll'),
    path('search',Search.as_view(),name='search')
]