from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import loginForm, registerForm, codeForm, ChangePassword, ResetPasswordForm, NewPasswordForm

urlpatterns = [
    path('login/', views.LoginView.as_view(form=loginForm), name='login'),
    path('register/', views.RegisterView.as_view(form=registerForm), name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('verify-email/', views.VerifyEmailView.as_view(form=codeForm), name='verify_email'),
    path('update-password/', views.ChangePasswordView.as_view(password_form=ChangePassword), name='update_password'),
    path('reset-password/', views.ResetPasswordView.as_view(form=ResetPasswordForm), name='reset_password'),
    path('reset-password/<uuid>/<verification_code>/', views.ResetPasswordConfirmView.as_view(form=NewPasswordForm), name='reset_password_confirm'),
]