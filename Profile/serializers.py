from rest_framework import serializers
from Profile.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile details.
    """
    first_name = serializers.CharField(
        source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'uuid',
            'first_name',
            'last_name',
            'email',
            'gender',
            'address',
            'profile_pic',
            'is_verified',
            'date_created',
            'date_updated'
        ]
        read_only_fields = ['uuid', 'email',
                            'is_verified', 'date_created', 'date_updated']


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile details, including the related User's first and last name.
    """
    first_name = serializers.CharField(
        source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name',
                  'gender', 'address', 'profile_pic']

    def validate_first_name(self, value):
        if value is None:
            return value
        v = value.strip()
        if not v:
            raise serializers.ValidationError("First name cannot be empty.")
        return v

    def validate_last_name(self, value):
        if value is None:
            return value
        v = value.strip()
        if not v:
            raise serializers.ValidationError("Last name cannot be empty.")
        return v

    def validate_gender(self, value):
        """Validate that gender is not empty if provided"""
        if value is not None:
            v = value.strip()
            if not v:
                raise serializers.ValidationError("Gender cannot be empty.")
            return v

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            first = user_data.get('first_name')
            last = user_data.get('last_name')
            if first is not None:
                user.first_name = first
            if last is not None:
                user.last_name = last
            user.save()

        # Update the UserProfile fields
        return super().update(instance, validated_data)
