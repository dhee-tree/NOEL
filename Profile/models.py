import uuid
from datetime import date
from django.db import models
from django.contrib.auth.models import User

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
    address = models.CharField(max_length=200, blank=True)
    profile_pic = models.CharField(max_length=200, blank=True)    
    password_changed = models.BooleanField(default=False)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)

    def save(self, *args, **kwargs):
        self.full_name = self.user.first_name + ' ' + self.user.last_name
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name