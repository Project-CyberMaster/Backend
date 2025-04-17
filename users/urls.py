from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/',include('django_rest_passwordreset.urls'), name="password_reset"),
    path('password-reset/verify/', views.ResetPasswordView.as_view(), name='verify_otp_reset_password'),
    path('profile/',views.ProfileDetail.as_view(), name='profile-update'),

]
