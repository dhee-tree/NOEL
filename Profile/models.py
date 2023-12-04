import uuid
from datetime import date
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SantaGroup(models.Model):
    group_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=50, unique=True)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)

    def __str__(self):
        return self.group_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.CharField(max_length=200, blank=True)    
    group_id = models.ForeignKey(SantaGroup, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username