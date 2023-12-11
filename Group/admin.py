from django.contrib import admin
from .models import SantaGroup, Pick, GroupMember

# Register your models here.
class SantaGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'group_code', 'is_open', 'created_by', 'date_created', 'date_updated')
    list_filter = ('is_open', 'created_by', 'date_created', 'date_updated')


class PickAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'picked_by', 'group_id', 'date_picked')
    list_filter = ('group_id', 'date_picked')


class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'user_profile_id', 'is_wrapped', 'date_created', 'date_updated')
    list_filter = ('date_created', 'is_wrapped')


admin.site.register(SantaGroup, SantaGroupAdmin)
admin.site.register(Pick, PickAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)