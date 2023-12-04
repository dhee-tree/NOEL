from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import codeForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name = "auth/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('2fa/', views.ConfirmView.as_view(form=codeForm), name='2fa'),
]