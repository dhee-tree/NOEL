from django.views import View
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from Profile.models import UserProfile
from .utils import authCodeGenerator, sendEmail
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Create your views here.
@method_decorator(login_required, name='dispatch')
class ConfirmView(View):
    template_name = 'auth/confirm.html'
    form = None

    def get(self, request):
        messages.info(request, 'Your need to login to access the 2FA page!')
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        user_profile.auth_code = authCodeGenerator()
        user_profile.save()

        sending_email = sendEmail(request, user, user_profile.auth_code)
        
        context = {'user': user, 'form': self.form}
        return render(request, self.template_name, context)
