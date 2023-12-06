from .models import UserProfile, Pick, SantaGroup
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

    def group_members_count(self):
        try:
            return UserProfile.objects.filter(group_id=self.get_profile().group_id).count()
        except ObjectDoesNotExist:
            return None

    def get_group_members_list(self):
        """Returns a list of all group members without the loggedin user and users who have not been picked"""
        try:
            group_list = list(UserProfile.objects.filter(group_id=self.get_profile().group_id).exclude(user=self.user).values_list('full_name', flat=True))
            for member in group_list:
                if Pick.objects.filter(group_id=self.get_profile().group_id, full_name=member).exists():
                    group_list.remove(member)
            return group_list
        except ObjectDoesNotExist:
            return None

    def set_picked(self, picked):
        """Sets the picked user to the loggedin user"""
        try:
            Pick.objects.create(group_id=self.get_profile().group_id, full_name=picked, picked_by=self.get_profile().full_name)
            return True
        except ObjectDoesNotExist:
            return False

    def get_picked(self):
        """Returns the picked user of the loggedin user"""
        try:
            return Pick.objects.get(picked_by=self.get_profile().full_name)
        except ObjectDoesNotExist:
            return None
