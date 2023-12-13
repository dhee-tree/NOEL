from . import views
from django.urls import path
from .forms import UpdateProfileForm

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('update-profile/', views.UpdateProfileView.as_view(form=UpdateProfileForm), name='update_profile'),
]
