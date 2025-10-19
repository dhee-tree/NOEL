from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, GoogleAuthSerializer, UserSerializer
from .managers import VerificationManager
from Mail.utils import MailManager

# For Google Auth
from google.oauth2 import id_token
from google.auth.transport import requests

# For JWT Tokens
from rest_framework_simplejwt.tokens import RefreshToken


class GoogleLoginAPIView(APIView):
    """
    API endpoint for handling Google Sign-In.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['id_token']

        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # You can also pass your Google Client ID here for extra security:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

        except ValueError:
            return Response({"error": "Invalid or expired Google token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract user info from the verified token
        google_user_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        gender = idinfo.get('gender', '')

        # "Get or Create" user logic
        try:
            # Case 1: User exists with this Google ID
            user = User.objects.get(userprofile__google_id=google_user_id)
        except User.DoesNotExist:
            try:
                # Case 2: User exists with this email, link their Google account
                user = User.objects.get(email=email)
                user.userprofile.google_id = google_user_id
                user.userprofile.gender = gender
                user.userprofile.is_verified = True
                user.userprofile.save()
            except User.DoesNotExist:
                # Case 3: No user found, create a new one
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                # Set an unusable password for users created via social auth
                user.set_unusable_password()
                user.save()
                user.userprofile.google_id = google_user_id
                user.userprofile.gender = gender
                user.userprofile.is_verified = True
                user.userprofile.save()

        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)

        # Prepare the response data
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.get_full_name(),
                'role': user.userprofile.role,
                'is_verified': user.userprofile.is_verified,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserRegistrationAPIView(generics.CreateAPIView):
    """
    API endpoint for creating (registering) a new user.
    Uses the UserRegistrationSerializer to handle all logic.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        verification_code = VerificationManager(
            user.userprofile).generate_verification_code()
        user.userprofile.verification_code = verification_code
        user.userprofile.save()

        MailManager(user.email).send_verification_email(
            user.first_name, verification_code)

        headers = self.get_success_headers(serializer.data)

        return Response(
            {"message": "Registration successful. Please check your email to verify your account."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class UserProfileView(APIView):
    """
    API endpoint to get the current authenticated user's profile.
    """
    # This permission ensures that only authenticated users can access this view.
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
