from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationAPIView.as_view(), name='register'),
    path('auth/google/', views.GoogleLoginAPIView.as_view(), name='google-auth'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
]
