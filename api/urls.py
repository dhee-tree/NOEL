from django.urls import include, path
from . import views
from Mail.views import ContactAPIView

urlpatterns = [
    path('auth/', include('Auth.urls')),
    path('contact/', ContactAPIView.as_view(), name='contact'),
    path('register/', views.UserRegistrationAPIView.as_view(), name='register'),
    path('auth/google/', views.GoogleLoginAPIView.as_view(), name='google-auth'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('groups/', include('Group.urls')),
    path('wishlists/', include('Wishlist.urls')),
    path('profile/', include('Profile.urls')),
]
