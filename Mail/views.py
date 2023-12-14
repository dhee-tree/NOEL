from django.views import View
from .utils import MailManager
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class PingUserView(LoginRequiredMixin, View):
    def get(self, request, email, group):
        mail_manager = MailManager(email)
        if  mail_manager.ping_user_email(group):
            messages.success(request, 'Ping sent successfully!')
            return redirect('group_unwrapped', group_name=group)
        else:
            messages.error(request, 'Ping failed! Please try again.')
            return redirect('group_unwrapped', group_name=group)