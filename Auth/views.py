from django.views import View
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from Profile.models import UserProfile
from Profile.views import GetUserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import VerificationManager
from Mail.utils import MailManager

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
                    login(request, user)
                    user_profile = UserProfile.objects.get(user=user)

                    return redirect('home')
        else:
            return render(request, self.template_name, {'form': post_form, 'formError': True})

@method_decorator(csrf_protect, name='dispatch')
class RegisterView(View):
    template_name = 'auth/register.html'
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
            username = post_form.cleaned_data.get('email')
            password = post_form.cleaned_data.get('password')
            email = post_form.cleaned_data.get('email')
            first_name = post_form.cleaned_data.get('first_name')
            last_name = post_form.cleaned_data.get('last_name')
            gender = post_form.cleaned_data.get('gender')
            address = post_form.cleaned_data.get('address')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                user.save()
                user_profile = UserProfile.objects.create(user=user, address=address, gender=gender)
                verification_code = VerificationManager(user_profile).generate_verification_code()
                user_profile.verification_code = verification_code
                user_profile.save()
                login(request, user)
                MailManager(email).send_verification_email(first_name, verification_code)
                messages.success(request, 'You have successfully registered. Please verify your account.')
                return redirect('home')
            else:
                context = {'form': post_form, 'registerError': True}
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, {'form': post_form, 'formError': True})


@method_decorator(csrf_protect, name='dispatch')
class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'auth/change-password.html'
    password_form = None

    def get(self, request):
        if request.user.is_staff:
            messages.error(request, 'You are not allowed to update password. Admins do not have a profile.')
            return redirect('admin:index')
        else:
            user_profile = GetUserProfile(request.user)
            context = {
                'user_profile': user_profile.get_profile(),
                'password_form': self.password_form,
            }
            return render(request, self.template_name, context)

    def post(self, request):
        post_form = self.password_form(request.POST)
        if post_form.is_valid():
            user = User.objects.get(username=request.user.username)
            new_password = request.POST.get('new_password')
            old_password = request.POST.get('old_password')
            user_password = check_password(old_password, user.password)
            if not user_password:
                messages.error(request, 'Invalid old password.')
                return redirect('update_password')
            else:
                if new_password == old_password:
                    messages.error(request, 'New password cannot be same as old password.')
                    return redirect('update_password')
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    user = authenticate(username=request.user.username, password=new_password)
                    login(request, user)

                    messages.success(request, 'You have successfully updated your password.')
                    return redirect('home')
        else:
            context = {
                'password_form': post_form,
            }
            return render(request, self.template_name, context)
