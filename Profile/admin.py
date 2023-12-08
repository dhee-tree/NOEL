from django.contrib import admin
from .models import SantaGroup, UserProfile, Pick

# Register your models here.
class SantaGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'group_code', 'date_created', 'date_updated')
    list_filter = ('date_created', 'date_updated')

class PickAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'picked_by', 'group_name', 'date_picked')
    list_filter = ('group_name', 'date_picked')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'profile_pic', 'group_name', 'is_wrapped', 'password_changed', 'auth_code', 'is_authenticated', 'date_created', 'date_updated')
    list_filter = ('group_name',)


admin.site.register(SantaGroup, SantaGroupAdmin)
admin.site.register(Pick, PickAdmin)
admin.site.register(UserProfile, UserProfileAdmin)