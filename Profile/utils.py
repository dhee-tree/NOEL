from .models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
import random

GREETINGS = [
    "Well done, you've been good! I have gift for you.",
    "Ah, just the person I was looking for—there is a gift for you!",
    "You've been so good this year! I have something special just for you.",
    "Here you go, a little something for being so wonderful!",
    "You've earned this—happy holidays and enjoy your gift!",
    "I have a special gift for you, just for being so good!",
    "You've been good this year, so here's a gift for you!",
    "You've been so good, I have a gift for you!",
]

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
        return f"Ho Ho Ho! {self.user.first_name}, {random.choice(GREETINGS)}"

    def update_profile(self, gender, address):
        """Updates the user profile of the loggedin user"""
        try:
            profile = UserProfile.objects.get(user=self.user)
            profile.gender=gender
            profile.address=address
            profile.save()
            return True
        except ObjectDoesNotExist:
            return False
