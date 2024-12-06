from django.contrib import admin
from .models import SantaGroup, Pick, GroupMember

# Register your models here.
class SantaGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'group_code', 'is_open', 'created_by', 'date_created', 'date_updated')
    list_filter = ('is_open', 'created_by', 'date_created', 'date_updated', 'is_archived')


class PickAdmin(admin.ModelAdmin):
    list_display = ('picked_by', 'group_id', 'date_picked')
    list_filter = ('group_id', 'date_picked', 'is_archived')


class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'user_profile_id', 'is_wrapped', 'date_created', 'date_updated')
    list_filter = ('group_id', 'is_wrapped', 'is_archived')


admin.site.register(SantaGroup, SantaGroupAdmin)
admin.site.register(Pick, PickAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)