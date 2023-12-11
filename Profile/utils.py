from .models import UserProfile
from Group.models import Pick
from django.core.exceptions import ObjectDoesNotExist

class GetUserProfile():
    def __init__(self, user):
        self.user = user

    def get_profile(self):
        """Returns the user profile of the loggedin user"""
        try:
            return UserProfile.objects.get(user=self.user)
        except ObjectDoesNotExist:
            return None

    def get_santa_greet(self):
        """Returns appropiate greeting based on the user gender"""
        if self.get_profile().gender == "Male":
            return 'a good boy'
        elif self.get_profile().gender == "Female":
            return 'a good girl'
        else:
            return 'good'
