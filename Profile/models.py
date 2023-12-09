import uuid
from datetime import date
from django.db import models
from Group.models import SantaGroup
from django.contrib.auth.models import User
from Auth.utils import authCodeGenerator

# Create your models here.
class UserProfile(models.Model):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Non-binary', 'Non-binary'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=11, choices=gender_choices, blank=True)
    profile_pic = models.CharField(max_length=200, blank=True)    
    group_id = models.ForeignKey(SantaGroup, on_delete=models.SET_NULL, null=True, blank=True)
    is_wrapped = models.BooleanField(default=True)
    password_changed = models.BooleanField(default=False)
    auth_code = models.CharField(max_length=6, default=authCodeGenerator)
    is_authenticated = models.BooleanField(default=False)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)

    def save(self, *args, **kwargs):
        self.full_name = self.user.first_name + ' ' + self.user.last_name
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username