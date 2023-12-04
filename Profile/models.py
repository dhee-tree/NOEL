import uuid
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from Auth.utils import authCodeGenerator

# Create your models here.
class SantaGroup(models.Model):
    group_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=50, unique=True)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)

    def __str__(self):
        return self.group_name

class UserProfile(models.Model):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Non-binary', 'Non-binary'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=11, choices=gender_choices, blank=True)
    profile_pic = models.CharField(max_length=200, blank=True)    
    group_id = models.ForeignKey(SantaGroup, on_delete=models.SET_NULL, null=True)
    is_wrapped = models.BooleanField(default=True)
    password_changed = models.BooleanField(default=False)
    auth_code = models.CharField(max_length=6, default=authCodeGenerator)
    is_authenticated = models.BooleanField(default=False)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)

    def __str__(self):
        return self.user.username