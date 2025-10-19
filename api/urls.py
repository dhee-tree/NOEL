from django.urls import include, path
from . import views

urlpatterns = [
    path('auth/', include('Auth.urls')),
    path('register/', views.UserRegistrationAPIView.as_view(), name='register'),
    path('auth/google/', views.GoogleLoginAPIView.as_view(), name='google-auth'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('groups/', include('Group.urls')),
]
