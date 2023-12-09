from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'profile_pic', 'group_id', 'is_wrapped', 'password_changed', 'auth_code', 'is_authenticated', 'date_created', 'date_updated')
    list_filter = ('group_id',)


admin.site.register(UserProfile, UserProfileAdmin)