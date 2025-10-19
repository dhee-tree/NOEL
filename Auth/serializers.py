from rest_framework import serializers
from Profile.models import UserProfile

class VerifyEmailSerializer(serializers.ModelSerializer):
    """
    Serializer for verifying email with a token.
    """
    token = serializers.CharField(write_only=True, source='verification_code')

    class Meta:
        model = UserProfile
        fields = ['token']
        extra_kwargs = {
            'token': {'write_only': True}
        }

    def validate_token(self, value):
        user_profile = UserProfile.objects.filter(verification_code=value).first()
        if not user_profile:
            raise serializers.ValidationError("Invalid verification code.")
        return value
    
    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.save()
        return instance
    


