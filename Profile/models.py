import uuid
from datetime import date
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Prefer not to say', 'Prefer not to say'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=50, choices=gender_choices, blank=True)
    address = models.CharField(max_length=200, blank=True)
    profile_pic = models.CharField(max_length=200, blank=True)    
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=8, blank=True, default='')
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)

    def save(self, *args, **kwargs):
        self.full_name = self.user.first_name + ' ' + self.user.last_name
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name
    

class WishListItem(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False)
    link = models.CharField(max_length=1000, null=True, blank=True)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['date_created']
        verbose_name_plural = 'Wish Lists Items'