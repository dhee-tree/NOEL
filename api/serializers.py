from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user. Handles password hashing.
    """
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    address = serializers.CharField(
        write_only=True, required=False, allow_blank=True)

    gender = serializers.CharField(
        write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name',
                  'password', 'password2', 'address', 'gender']
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.userprofile.address = validated_data.get('address', '')
        user.userprofile.gender = validated_data.get('gender', '')
        user.userprofile.save()
        return user


class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for validating the Google ID token sent from the frontend.
    """
    id_token = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, including basic profile info.
    """

    role = serializers.CharField(source='userprofile.role', read_only=True)
    is_verified = serializers.BooleanField(
        source='userprofile.is_verified', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'role', 'is_verified']
