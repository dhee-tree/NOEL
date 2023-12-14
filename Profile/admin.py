from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'address', 'gender', 'profile_pic', 'is_verified', 'verification_code', 'date_created', 'date_updated')
    list_filter = ('gender',)


admin.site.register(UserProfile, UserProfileAdmin)