from django.contrib import admin
from .models import UserProfile, WishListItem

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'address', 'gender', 'profile_pic', 'is_verified', 'verification_code', 'date_created', 'date_updated')
    list_filter = ('gender',)

class WishListItemAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'name', 'link', 'date_created', 'date_updated')
    list_filter = ('date_created',)


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(WishListItem, WishListItemAdmin)