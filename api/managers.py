import random
import string
from django.core.exceptions import ObjectDoesNotExist


class VerificationManager():
    def __init__(self, profile):
        self.profile = profile

    def get_user_verification_code(self):
        """Returns the user's verification code"""
        return self.profile.verification_code

    def generate_verification_code(self):
        """Generates verification code for a user"""
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

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

    def check_user_verified(self):
        """Checks if the user is verified"""
        return self.profile.is_verified

    def reset_verification_status(self):
        self.profile.is_verified = False
        self.profile.save()
        return True
