from django.views import View
from rest_framework.response import Response
from Auth.serializers import VerifyEmailSerializer
from Mail.utils import MailManager
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from .utils import VerificationManager
from Profile.models import UserProfile
from Profile.views import GetUserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics, permissions, status
from rest_framework.views import APIView

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
        invalid_details_message = "Your email or password is incorrect. Please try again or reset your password."
        if post_form.is_valid():
            username = post_form.cleaned_data.get('email').lower()
            password = post_form.cleaned_data.get('password')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, invalid_details_message)
                return render(request, self.template_name, {'form': post_form})
            else:
                if not check_password(password, user.password):
                    messages.error(request, invalid_details_message)
                    return render(request, self.template_name, {'form': post_form})
                else:
                    user = authenticate(
                        request, username=username, password=password)
                    login(request, user)
                    user_profile = UserProfile.objects.get(user=user)

                    return redirect('home')
        else:
            messages.error(request, invalid_details_message)
            return render(request, self.template_name, {'form': post_form})


@method_decorator(csrf_protect, name='dispatch')
class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'auth/change-password.html'
    password_form = None

    def get(self, request):
        if request.user.is_staff:
            messages.error(
                request, 'You are not allowed to update password. Admins do not have a profile.')
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
                    messages.error(
                        request, 'New password cannot be same as old password.')
                    return redirect('update_password')
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    user = authenticate(
                        username=request.user.username, password=new_password)
                    login(request, user)

                    messages.success(
                        request, 'You have successfully updated your password.')
                    return redirect('home')
        else:
            context = {
                'password_form': post_form,
            }
            return render(request, self.template_name, context)


class VerifyEmailView(APIView):
    """
    View to handle email verification.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token):
        try:
            user_profile = UserProfile.objects.get(verification_code=token)
        except UserProfile.DoesNotExist:
            return Response({"errors": {"token": ["Invalid verification code."]}}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = VerifyEmailSerializer(user_profile, data={'token': token})
        if serializer.is_valid():
            serializer.update(user_profile, serializer.validated_data)
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, name='dispatch')
class ResetPasswordView(View):
    template_name = 'auth/reset-password.html'
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
            email = post_form.cleaned_data.get('email').lower()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Invalid email.')
                return redirect('reset_password')
            else:
                user_profile = UserProfile.objects.get(user=user)
                verification_manager = VerificationManager(user_profile)
                verification_manager.reset_verification_status()
                verification_code = verification_manager.generate_verification_code()
                user_profile.verification_code = verification_code
                user_profile.save()
                MailManager(email).send_reset_password_email(
                    name=user.first_name, uuid=user_profile.uuid, verification_code=verification_code)
                messages.success(
                    request, 'We have sent you an email with instructions to reset your password.')
                return redirect('login')
        else:
            return render(request, self.template_name, {'form': post_form})


@method_decorator(csrf_protect, name='dispatch')
class ResetPasswordConfirmView(View):
    template_name = 'auth/reset-password-confirm.html'
    form = None

    def get(self, request, uuid, verification_code):
        user_profile = UserProfile.objects.get(uuid=uuid)
        if user_profile:
            context = {'form': self.form}
            return render(request, self.template_name, context)
        else:
            messages.error(request, 'Invalid reset password link.')
            return redirect('login')

    def post(self, request, uuid, verification_code):
        user_profile = UserProfile.objects.get(
            uuid=uuid)
        if user_profile:
            post_form = self.form(request.POST)
            if post_form.is_valid():
                match_password = post_form.check_password()

                if not match_password:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, self.template_name, {'form': post_form})

                if not VerificationManager(user_profile).verify_user(verification_code):
                    messages.error(request, 'Invalid verification code.')
                    return redirect('login')

                new_password = post_form.cleaned_data.get('password')

                user = User.objects.get(email=user_profile.user.email)
                user.set_password(new_password)
                user.save()
                user = authenticate(username=user.username,
                                    password=new_password)
                login(request, user)
                messages.success(
                    request, 'You have successfully reset your password.')
                MailManager(user.email).send_reset_password_confirm_email(
                    name=user.first_name)
                return redirect('home')
            else:
                context = {'form': post_form, 'formError': True}
                messages.error(
                    request, 'Password must contain 8 characters, including 1 uppercase letter, 1 lowercase letter, 1 number.')
                return render(request, self.template_name, context)
        else:
            messages.error(request, 'Invalid reset password link.')
            return redirect('login')
