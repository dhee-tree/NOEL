from django.views import View
from .utils import MailManager
from django.contrib import messages
from Profile.models import UserProfile
from Auth.utils import VerificationManager
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.html import strip_tags
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings

# Create your views here.


class PingUserView(LoginRequiredMixin, View):
    def get(self, request, email, group):
        mail_manager = MailManager(email)
        if mail_manager.ping_user_address(group):
            messages.success(request, 'Ping sent successfully!')
            return redirect('group_unwrapped', group_name=group)
        else:
            messages.error(request, 'Ping failed! Please try again.')
            return redirect('group_unwrapped', group_name=group)


class ResendVerificationView(LoginRequiredMixin, View):
    def get(self, request):
        email = request.user.email
        first_name = request.user.first_name
        verification_code = VerificationManager(UserProfile.objects.get(
            user=request.user)).get_user_verification_code()
        mail_manager = MailManager(email)
        if mail_manager.send_verification_email(first_name, verification_code):
            messages.success(request, 'Verification email sent successfully!')
            return redirect('resend_code')
        else:
            messages.error(
                request, 'Verification email failed! Please try again.')
            return redirect('resend_code')


class ContactAPIView(APIView):
    """Public contact endpoint. Accepts name, email, subject, message."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data or {}
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if getattr(settings, 'APP_ENV', 'development') != 'production':
            subject = f"{settings.APP_ENV.upper()} - {subject}"

        if not name or not email or not message:
            return Response({"error": "name, email and message are required."}, status=status.HTTP_400_BAD_REQUEST)

        # basic email validation
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

        mail_manager = MailManager(email)
        sent = mail_manager.send_contact_message(
            name=name, message=message, subject=subject)
        if sent:
            return Response({"detail": "Message sent."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send message."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
