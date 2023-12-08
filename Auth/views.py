from django.views import View
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from Profile.models import UserProfile
from django.contrib.auth.models import User
from .utils import authCodeGenerator, sendEmail
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required

# Create your views here.
class LoginView(View):
    template_name = 'auth/login.html'
    form = None

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            context = {'form': self.form}
            return render(request, self.template_name, context)

    def post(self, request):
        post_form = self.form(request.POST)
        if post_form.is_valid():
            username = post_form.cleaned_data.get('username')
            password = post_form.cleaned_data.get('password')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return render(request, self.template_name, {'form': post_form, 'userError': True})
            else:
                if not check_password(password, user.password):
                    return render(request, self.template_name, {'form': post_form, 'passwordError': True})
                else:
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        user_profile = UserProfile.objects.get(user=user)
                        if user_profile.auth_code == None:
                            user_profile.auth_code = authCodeGenerator()
                            user_profile.save()
                        sending_email = sendEmail(request, user, user_profile.auth_code)
                        return redirect('2fa')
        else:
            return render(request, self.template_name, {'form': post_form, 'formError': True})
        


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class ConfirmView(View):
    template_name = 'auth/confirm.html'
    form = None

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            messages.info(request, 'Your need to login to access the 2FA page!')
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            user_profile.auth_code = authCodeGenerator()
            user_profile.save()

            sending_email = sendEmail(request, user, user_profile.auth_code)

            context = {'user': user, 'form': self.form}
            return render(request, self.template_name, context)
        
    def post(self, request):
        post_form = self.form(request.POST)
        code = request.POST.get('code')
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        if code == user_profile.auth_code:
            return redirect('home')
        else:
            return render(request, self.template_name, {'form': post_form, 'code_error': True})