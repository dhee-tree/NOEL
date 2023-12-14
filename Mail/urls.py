from . import views
from django.urls import path

urlpatterns = [
    path('ping/<str:email>/<str:group>', views.PingUserView.as_view(), name='mail_ping'),
]