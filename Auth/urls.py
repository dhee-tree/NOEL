from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import loginForm, registerForm, codeForm, ChangePassword

urlpatterns = [
    path('login/', views.LoginView.as_view(form=loginForm), name='login'),
    path('register/', views.RegisterView.as_view(form=registerForm), name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('update-password/', views.ChangePasswordView.as_view(password_form=ChangePassword), name='update_password'),
]