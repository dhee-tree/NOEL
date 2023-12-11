from . import views
from django.urls import path

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='group_home'),
    path('create/', views.CreateGroupView.as_view(), name='group_create'),
    path('view/<str:group_name>/', views.ViewGroupView.as_view(), name='group_view'),
]
