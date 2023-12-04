from .models import UserProfile
from django.core.exceptions import ObjectDoesNotExist

class GetUserProfile():
    def __init__(self, user):
        self.user = user

    def get_profile(self):
        try:
            return UserProfile.objects.get(user=self.user)
        except UserProfile.ObjectDoesNotExist:
            return None

    def group_members_count(self):
        try:
            return UserProfile.objects.filter(group_id=self.get_profile().group_id).count()
        except UserProfile.ObjectDoesNotExist:
            return None

    def getSantaGreet(self):
        if self.get_profile().gender == "Male":
            return 'a good boy'
        elif self.get_profile().gender == "Female":
            return 'a good girl'
        else:
            return 'good'
