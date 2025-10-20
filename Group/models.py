import uuid
from datetime import date
from django.db import models

# Create your models here.


class SantaGroup(models.Model):
    # Basic fields
    group_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=50, unique=True)
    group_code = models.CharField(max_length=6, unique=True, default='')
    is_open = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'Profile.UserProfile', on_delete=models.SET_NULL, null=True)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    # Date fields for event scheduling
    assignment_reveal_date = models.DateTimeField(
        null=True, blank=True, help_text="When participants can see their assigned person")
    gift_exchange_deadline = models.DateTimeField(
        null=True, blank=True, help_text="Final date for gift exchange")
    wishlist_deadline = models.DateTimeField(
        null=True, blank=True, help_text="Deadline for submitting wishlists")
    join_deadline = models.DateTimeField(
        null=True, blank=True, help_text="Last date to join the group")

    # Budget configuration
    budget_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Minimum budget amount")
    budget_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum budget amount")
    budget_currency = models.CharField(
        max_length=3, default='GBP', help_text="Currency code (GBP, USD, EUR, etc.)")

    # Additional group information
    description = models.TextField(
        blank=True, null=True, help_text="Group description or rules")
    exchange_location = models.CharField(
        max_length=255, blank=True, null=True, help_text="Physical or virtual location for exchange")

    # Theme choices
    THEME_CHOICES = [
        ('christmas', 'Christmas'),
        ('winter', 'Winter Holiday'),
        ('office', 'Office Party'),
        ('family', 'Family'),
        ('friends', 'Friends'),
        ('general', 'General'),
    ]
    theme = models.CharField(max_length=20, choices=THEME_CHOICES,
                             default='general', help_text="Group theme or category")

    def __str__(self):
        return self.group_name


class Pick(models.Model):
    pick_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=50, blank=False)
    picked_by = models.CharField(max_length=255, blank=False)
    group_id = models.ForeignKey(
        SantaGroup, on_delete=models.CASCADE, null=True, blank=False)
    date_picked = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('full_name', 'group_id')

    def __str__(self):
        return self.full_name


class GroupMember(models.Model):
    group_id = models.ForeignKey(SantaGroup, on_delete=models.CASCADE)
    user_profile_id = models.ForeignKey(
        'Profile.UserProfile', on_delete=models.CASCADE)
    is_wrapped = models.BooleanField(default=True)
    date_created = models.DateField(default=date.today)
    date_updated = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.group_id.group_name + ' - ' + self.user_profile_id.user.username

    class Meta:
        unique_together = ('group_id', 'user_profile_id')
