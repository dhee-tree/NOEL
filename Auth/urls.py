from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import loginForm, codeForm

urlpatterns = [
    path('login/', views.LoginView.as_view(form=loginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('2fa/', views.ConfirmView.as_view(form=codeForm), name='2fa'),
]