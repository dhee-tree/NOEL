import uuid
from datetime import date
from django.db import models

# Create your models here.
class SantaGroup(models.Model):
    group_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=50, unique=True)
    group_code = models.CharField(max_length=6, unique=True, default='')
    is_open = models.BooleanField(default=True)
    created_by = models.ForeignKey('Profile.UserProfile', on_delete=models.SET_NULL, null=True)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name


class Pick(models.Model):
    pick_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=50, blank=False)
    picked_by = models.CharField(max_length=255, blank=False)
    group_id = models.ForeignKey(SantaGroup, on_delete=models.CASCADE, null=True, blank=False)
    date_picked = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('full_name', 'group_id')

    def __str__(self):
        return self.full_name


class GroupMember(models.Model):
    group_id = models.ForeignKey(SantaGroup, on_delete=models.CASCADE)
    user_profile_id = models.ForeignKey('Profile.UserProfile', on_delete=models.CASCADE)
    is_wrapped = models.BooleanField(default=True)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.group_id.group_name + ' - ' + self.user_profile_id.user.username

    class Meta:
        unique_together = ('group_id', 'user_profile_id')
