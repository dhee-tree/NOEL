from django.views import View
from .utils import MailManager
from django.contrib import messages
from Profile.models import UserProfile
from Auth.utils import VerificationManager
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class PingUserView(LoginRequiredMixin, View):
    def get(self, request, email, group):
        mail_manager = MailManager(email)
        if mail_manager.ping_user_email(group):
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
