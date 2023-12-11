from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'profile_pic', 'password_changed', 'date_created', 'date_updated')
    list_filter = ('gender',)


admin.site.register(UserProfile, UserProfileAdmin)