from rest_framework import serializers
from .models import Wishlist, WishlistItem
from Group.models import SantaGroup


class WishlistItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual wishlist items.
    """
    class Meta:
        model = WishlistItem
        fields = [
            'item_id',
            'name',
            'description',
            'link',
            'store',
            'price_estimate',
            'priority',
            'is_public',
            'is_purchased',
            'date_created',
            'date_updated'
        ]
        read_only_fields = ['item_id', 'date_created', 'date_updated']


class CreateUpdateWishlistItemSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating wishlist items.
    """
    class Meta:
        model = WishlistItem
        fields = ['name', 'link', 'store', 'description',
                  'price_estimate', 'priority', 'is_public', 'is_purchased']

    def validate_name(self, value):
        """Validate that item name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Item name cannot be empty.")
        return value.strip()


class CreateWishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a wishlist.
    """
    class Meta:
        model = Wishlist
        fields = ['group']

    def validate_group(self, value):
        """Validate that the group exists"""
        if not SantaGroup.objects.filter(group_id=value.group_id).exists():
            raise serializers.ValidationError("Group does not exist.")
        return value


class WishlistListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing wishlists with essential details.
    """
    class Meta:
        model = Wishlist
        fields = [
            'wishlist_id',
            'name',
            'date_created',
            'date_updated'
        ]
        read_only_fields = ['wishlist_id', 'name',
                            'date_created', 'date_updated']


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for wishlist with items.
    """
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'wishlist_id',
            'name',
            'items',
            'date_created',
            'date_updated'
        ]
        read_only_fields = ['wishlist_id', 'name',
                            'date_created', 'date_updated']
