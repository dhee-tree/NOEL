from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import loginForm, registerForm, codeForm, ChangePassword, ResetPasswordForm, NewPasswordForm
from .views import VerifyEmailView

urlpatterns = [
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', views.PasswordResetRequestAPIView.as_view(), name='api_reset_password'),
    path('reset-password/confirm/', views.PasswordResetConfirmAPIView.as_view(), name='api_reset_password_confirm'),
    path('reset-password/validate/', views.PasswordResetValidateAPIView.as_view(), name='api_reset_password_validate'),
    # V1 Routes
    path('register/', views.RegisterView.as_view(form=registerForm), name='v1_register'),
    path('login/', views.LoginView.as_view(form=loginForm), name='v1_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='v1_logout'),
    path('update-password/', views.V1_ChangePasswordView.as_view(password_form=ChangePassword), name='v1_update_password'),
    # path('reset-password/', views.ResetPasswordView.as_view(form=ResetPasswordForm), name='reset_password'),
    # path('reset-password/<uuid>/<verification_code>/', views.ResetPasswordConfirmView.as_view(form=NewPasswordForm), name='reset_password_confirm'),
]