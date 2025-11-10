from django.contrib import admin
from .models import Wishlist, WishlistItem

# Register your models here.


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'group', 'date_created', 'date_updated')
    list_filter = ('date_created',)


class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('wishlist', 'name', 'link', 'store',
                    'date_created', 'date_updated')
    list_filter = ('date_created',)


admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(WishlistItem, WishlistItemAdmin)
