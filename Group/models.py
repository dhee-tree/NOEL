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
    gift_exchange_deadline = models.DateTimeField(
        null=True, blank=True, help_text="Final date for gift exchange")
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

    # White Elephant mode
    is_white_elephant = models.BooleanField(
        default=False, help_text="Enable White Elephant mode (gift stealing)")
    
    # The Snatcher (Phase 2)
    snatcher_user_id = models.IntegerField(
        null=True, 
        blank=True,
        help_text="The user chosen as The Snatcher"
    )
    snatch_revealed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When The Snatcher was revealed to them"
    )
    snatcher_notified = models.BooleanField(
        default=False,
        help_text="Has The Snatcher been notified?"
    )

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
    full_name = models.CharField(max_length=50, null=True, blank=True)
    picked_by_profile = models.ForeignKey(
        'Profile.UserProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='picks_made')
    picked_profile = models.ForeignKey(
        'Profile.UserProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='picks_received')
    group_id = models.ForeignKey(
        SantaGroup, on_delete=models.CASCADE, null=True, blank=False)
    date_picked = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group_id', 'picked_profile'], name='unique_pick_per_group'),
        ]

    def __str__(self):
        # Prefer the picked profile's username when available, else fallback to picker's username
        try:
            if self.picked_profile and getattr(self.picked_profile, 'user', None):
                return self.picked_profile.user.username
        except Exception:
            pass
        try:
            if self.picked_by_profile and getattr(self.picked_by_profile, 'user', None):
                return self.picked_by_profile.user.username
        except Exception:
            pass
        return str(self.pick_id)


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
