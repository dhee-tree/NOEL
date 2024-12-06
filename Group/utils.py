import random, string
from django.db import IntegrityError
from Profile.models import UserProfile, WishListItem
from .models import SantaGroup, GroupMember, Pick
from django.core.exceptions import ObjectDoesNotExist


class GroupManager():
    """Class to manage groups"""
    def __init__(self, user):
        self.user = user

    def groupJoinCode(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    def create_group(self, group_name):
        """Create a new group by the loggedin user"""
        try:
            group_code = self.groupJoinCode()
            new_group = SantaGroup.objects.create(group_name=group_name, group_code=group_code, created_by=self.user.userprofile)
            GroupMember.objects.create(group_id=new_group, user_profile_id=self.user.userprofile)
            return True
        except IntegrityError:
            return False
        except ObjectDoesNotExist:
            return False

    def user_group(self):
        """Returns the group of any user"""
        try:
            return GroupMember.objects.filter(user_profile_id=self.user.userprofile, group_id__is_archived=False)
        except ObjectDoesNotExist:
            return None

    def check_group_code(self, group_code):
        """Checks if the group code is valid"""
        try:
            return SantaGroup.objects.filter(group_code=group_code).exists()
        except ObjectDoesNotExist:
            return False

    def join_group(self, group_code):
        """Adds the loggedin user to a group"""
        try:
            group = SantaGroup.objects.get(group_code=group_code)
            if not self.get_is_open(group):
                return False
            if group.is_archived:
                return False
            else:
                GroupMember.objects.create(group_id=group, user_profile_id=self.user.userprofile)
                return True
        except ObjectDoesNotExist:
            return False
        except IntegrityError:
            return False

    def check_group_creator(self, group):
        """Checks if the loggedin user is the creator of the group"""
        try:
            SantaGroup.objects.filter(group_name=group).values('created_by').get(created_by=self.user.userprofile)
            return True
        except ObjectDoesNotExist:
            return False

    def check_group_member(self, group):
        """Checks if the loggedin user is a member of the group"""
        try:
            GroupMember.objects.get(group_id=group, user_profile_id=self.user.userprofile)
            return True
        except ObjectDoesNotExist:
            return False

    def get_group_members_list(self, group):
        """Returns a list of all group members without the loggedin user and users who have not been picked"""
        try:
            group_list = list(GroupMember.objects.filter(group_id=group).exclude(user_profile_id=self.user.userprofile).values_list('user_profile_id__full_name', flat=True))
            for member in group_list:
                if Pick.objects.filter(group_id=group, full_name=member).exists():
                    group_list.remove(member)
            return group_list
        except ObjectDoesNotExist:
            return None

    def get_is_open(self, group):
        """Returns the open status of the group"""
        try:
            return SantaGroup.objects.get(group_name=group).is_open
        except ObjectDoesNotExist:
            return None

    def set_is_open(self, group, status):
        """Sets the open status of the group"""
        try:
            santa_group = SantaGroup.objects.get(group_name=group)
            santa_group.is_open = status
            santa_group.save()
            return True
        except ObjectDoesNotExist:
            return False
    
    # Check user wrapped status
    def get_wrapped(self, group):
        """Returns Boolean value if user has opened their wrapped or not"""
        try:
            return GroupMember.objects.filter(group_id=group, user_profile_id=self.user.userprofile).get().is_wrapped
        except ObjectDoesNotExist:
            return None

    # Picking
    def set_picked(self, group, picked):
        """Sets the picked user to the loggedin user"""
        try:
            Pick.objects.create(group_id=group, full_name=picked, picked_by=self.user.userprofile.full_name)
            return True
        except ObjectDoesNotExist:
            return False

    def get_picked(self, group):
        """Returns the picked user of the loggedin user"""
        try:
            return Pick.objects.get(group_id=group, picked_by=self.user.userprofile.full_name).full_name
        except ObjectDoesNotExist:
            return None

    def get_picked_address(self, group):
        """Returns the picked user address of the loggedin user"""
        try:
            return UserProfile.objects.get(full_name=self.get_picked(group)).address
        except ObjectDoesNotExist:
            return None

    def get_picked_email(self, group):
        """Returns the picked user email of the loggedin user"""
        try:
            return UserProfile.objects.get(full_name=self.get_picked(group)).user.email
        except ObjectDoesNotExist:
            return None
        
    def get_picked_user_wishlist(self, group):
        """Returns the wishlist of the picked user"""
        try:
            return WishListItem.objects.filter(user_profile=UserProfile.objects.get(full_name=self.get_picked(group)))
        except ObjectDoesNotExist:
            return None

    def check_pick(self, group):
        """Checks if the logged in user has been picked a participant"""
        try:
            Pick.objects.get(picked_by=self.user.userprofile.full_name, group_id=group)
            return True
        except ObjectDoesNotExist:
            return False