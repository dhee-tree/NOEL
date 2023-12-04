from . import views
from django.urls import path


urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('wrapped/', views.WrappedView.as_view(), name='wrapped'),
    path('unwrapped/', views.UnwrappedView.as_view(), name='unwrapped'),
]
