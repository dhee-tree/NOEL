from . import views
from django.urls import path

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='group_home'),
    path('create/', views.CreateView.as_view(), name='group_create'),
]
