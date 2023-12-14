import random, string
from django.core.exceptions import ObjectDoesNotExist


class VerificationManager():
    def __init__(self, profile):
        self.profile = profile

    def generate_verification_code(self):
        """Generates verification code for a user"""
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    def verify_user(self, verification_code):
        """Verifies the user"""
        try:
            if self.profile.verification_code == verification_code:
                self.profile.is_verified = True
                self.profile.save()
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

# class VerificationTokenGenerator(PasswordResetTokenGenerator):
#     def _make_hash_value(self, user, timestamp):
#         return (
#             six.text_type(user.pk) + six.text_type(timestamp) +
#             six.text_type(user.is_active)
#         )
# account_activation_token = VerificationTokenGenerator()