from django.urls import path
from .views import *

urlpatterns=[
    path('',ExamList.as_view(),name='list-exams'),
    path('<int:pk>',GetExam.as_view(),name='get-exam'),
    path('<int:pk>/questions',QuestionList.as_view(),name='get-questions'),
    path('<int:pk>/questions/<int:order_index>',GetQuestion.as_view(),name='get-question'),
    path('<int:pk>/start',StartExam.as_view(),name='start-exam'),
    path('<int:pk>/finish',FinishExam.as_view(),name='finish-exam'),
    path('<int:pk>/answer',SubmitAnswer.as_view(),name='submit-answer'),
]