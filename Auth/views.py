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
from rest_framework import permissions, status
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import permissions
from django.conf import settings

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
            username = post_form.cleaned_data.get('email').lower()
            password = post_form.cleaned_data.get('password')
            email = post_form.cleaned_data.get('email').lower()
            first_name = post_form.cleaned_data.get('first_name')
            last_name = post_form.cleaned_data.get('last_name')
            gender = post_form.cleaned_data.get('gender')
            address = post_form.cleaned_data.get('address')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                user.save()
                user_profile = UserProfile.objects.create(
                    user=user, address=address, gender=gender)
                verification_code = VerificationManager(
                    user_profile).generate_verification_code()
                user_profile.verification_code = verification_code
                user_profile.save()
                login(request, user)
                MailManager(email).send_verification_email(
                    first_name, verification_code)
                messages.success(
                    request, 'You have successfully registered. Please verify your account.')
                return redirect('home')
            else:
                context = {'form': post_form, 'registerError': True}
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, {'form': post_form, 'formError': True})


@method_decorator(csrf_protect, name='dispatch')
class V1_ChangePasswordView(LoginRequiredMixin, View):
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

##############################
# API VIEWS
##############################


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


class ChangePasswordView(APIView):
    """
    API endpoint for changing the authenticated user's password.
    POST /api/change-password/ - Change password
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Change the authenticated user's password"""
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return Response(
                {"error": "Current, new, and confirm passwords are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response(
                {"error": "New password and confirm password do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if not user.check_password(current_password):
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if current_password == new_password:
            return Response(
                {"error": "New password cannot be the same as the old password."},
                status=status.HTTP_409_CONFLICT
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK
        )


class PasswordResetRequestAPIView(APIView):
    """API endpoint to request a password reset.
    
        Rate-limited via throttle_scope 'password_reset' to reduce abuse and enumeration.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        if not email:
            return Response({"detail": "If an account exists, we've sent reset instructions."}, status=status.HTTP_200_OK)

        email = email.lower().strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If an account exists, we've sent reset instructions."}, status=status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        MailManager(user).send_reset_password_email(name=user.first_name, uid=uid, token=token)

        return Response({"detail": "If an account exists, we've sent reset instructions."}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    """API endpoint to confirm password reset. Accepts `uid`, `token`, `new_password`, `confirm_password`."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get('uid') or request.data.get('uidb64')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not uidb64 or not token or not new_password or not confirm_password:
            return Response({"error": "uid, token and new passwords are required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid reset link or token."}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        try:
            MailManager(user).send_reset_password_confirm_email(
                name=user.first_name)
        except Exception:
            pass

        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)


class PasswordResetValidateAPIView(APIView):
    """Validate a uid/token pair so the frontend can pre-check links.

    GET parameters: `uid` (uidb64), `token`.
    Returns 200 with {"valid": true} if token is valid, 400 with {"valid": false, "error": "..."} otherwise.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        uidb64 = request.query_params.get(
            'uid') or request.query_params.get('uidb64')
        token = request.query_params.get('token')

        if not uidb64 or not token:
            return Response({"valid": False, "error": "uid and token are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"valid": False, "error": "Invalid uid."}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({"valid": False, "error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"valid": True}, status=status.HTTP_200_OK)
