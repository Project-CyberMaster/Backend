from django.urls import path
from .views import *

urlpatterns=[
    path('<int:pk>',GetCert.as_view(),name='get-cert'),
    path('validate/<str:id>',Validate.as_view(),name='get-cert'),
    path('',CertificationList.as_view(),name='certification-list'),
]  