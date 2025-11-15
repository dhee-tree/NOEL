from django.db import models
import uuid


class Priority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'


class Wishlist(models.Model):
    wishlist_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    user_profile = models.ForeignKey(
        'Profile.UserProfile', on_delete=models.CASCADE)
    group = models.ForeignKey('Group.SantaGroup', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_profile', 'group')
        ordering = ['-date_updated']

    def save(self, *args, **kwargs):
        self.name = f"{self.group.group_name} Wishlist"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_profile.full_name}'s wishlist for {self.group.group_name}"


class WishlistItem(models.Model):
    item_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=1000, null=True, blank=True)
    store = models.CharField(max_length=255, null=True, blank=True)
    price_estimate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    priority = models.CharField(
        max_length=6, choices=Priority.choices, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_purchased = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_created']
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return self.name
