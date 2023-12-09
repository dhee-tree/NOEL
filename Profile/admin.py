from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'profile_pic', 'is_wrapped', 'password_changed', 'date_created', 'date_updated')
    list_filter = ('is_wrapped',)


admin.site.register(UserProfile, UserProfileAdmin)