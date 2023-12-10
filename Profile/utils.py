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

    def get_wrapped(self):
        """Returns Boolean value if user has opened their wrapped or not"""
        try:
            return UserProfile.objects.get(user=self.user).is_wrapped
        except ObjectDoesNotExist:
            return None

    def set_wrapped(self):
        """Sets the wrapped value of the loggedin user to False"""
        try:
            UserProfile.objects.filter(user=self.user).update(is_wrapped=False)
            return True
        except ObjectDoesNotExist:
            return False
