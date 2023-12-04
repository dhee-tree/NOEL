from django.contrib import admin
from .models import SantaGroup, UserProfile

# Register your models here.
class SantaGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'date_created', 'date_updated')
    list_filter = ('date_created', 'date_updated')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic', 'group_id', 'password_changed', 'auth_code', 'date_created', 'date_updated')
    list_filter = ('group_id',)

admin.site.register(SantaGroup, SantaGroupAdmin)
admin.site.register(UserProfile, UserProfileAdmin)