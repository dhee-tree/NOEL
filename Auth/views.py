from django.views import View
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from Profile.models import UserProfile
from django.contrib.auth.models import User
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
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                user.save()
                user_profile = UserProfile.objects.create(user=user, gender=gender)
                user_profile.save()
                login(request, user)
                return redirect('home')
            else:
                context = {'form': post_form, 'registerError': True}
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, {'form': post_form, 'formError': True})
