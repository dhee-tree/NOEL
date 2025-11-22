from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Wishlist, WishlistItem
from .serializers import (
    WishlistSerializer,
    WishlistListSerializer,
    WishlistItemSerializer,
    CreateWishlistSerializer,
    CreateUpdateWishlistItemSerializer,
)
from Group.utils import GroupManager
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from Mail.utils import MailManager
from Group.models import Pick, GroupMember


class WishlistListCreateAPIView(APIView):
    """
    API endpoint for listing user's wishlists and creating a new wishlist.
    GET /wishlists - Returns all wishlists for the authenticated user
    POST /wishlists - Creates a new wishlist for a specific group
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return all wishlists for the authenticated user"""
        user_profile = request.user.userprofile
        wishlists = Wishlist.objects.filter(user_profile=user_profile)
        serializer = WishlistListSerializer(wishlists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a new wishlist for a group"""
        serializer = CreateWishlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_profile = request.user.userprofile
        group = serializer.validated_data['group']

        group_manager = GroupManager(request.user)
        if not group_manager.check_group_member(group):
            return Response(
                {"error": "You must be a member of this group to create a wishlist."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if wishlist already exists for this user and group
        if Wishlist.objects.filter(user_profile=user_profile, group=group).exists():
            return Response(
                {
                    "error": "Wishlist already exists for this group.",
                },
                status=status.HTTP_409_CONFLICT
            )

        # Create the wishlist
        wishlist = Wishlist.objects.create(
            user_profile=user_profile,
            group=group
        )

        response_serializer = WishlistSerializer(wishlist)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class WishlistDetailAPIView(generics.RetrieveDestroyAPIView):
    """
    API endpoint for retrieving and deleting a specific wishlist.
    GET /wishlists/<id> - Returns wishlist details with items
    DELETE /wishlists/<id> - Deletes wishlist (only owner can delete)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer
    lookup_field = 'wishlist_id'

    def get_queryset(self):
        """Base queryset: all wishlists. Permission checks are applied in `get_object`."""
        return Wishlist.objects.all()

    def get_object(self):
        """Retrieve the wishlist and enforce access: owner OR a user who picked this profile in the same group."""
        wishlist = get_object_or_404(Wishlist, wishlist_id=self.kwargs.get('wishlist_id'))

        user_profile = self.request.user.userprofile
        # Owner always allowed
        if wishlist.user_profile == user_profile:
            return wishlist

        # Allow if requester picked this wishlist owner in the same group
        from Group.models import Pick
        picked = Pick.objects.filter(
            group_id=wishlist.group,
            picked_by_profile=self.request.user.userprofile,
            picked_profile=wishlist.user_profile,
        ).exists()

        if picked:
            return wishlist

        # Not allowed
        raise PermissionDenied('You do not have permission to view this wishlist.')

    def retrieve(self, request, *args, **kwargs):
        """Return wishlist details. Owners see all items; pickers see only public items."""
        wishlist = self.get_object()
        user_profile = request.user.userprofile

        serializer = WishlistSerializer(wishlist)
        data = serializer.data

        # If requester is not the owner, filter items to public only
        if wishlist.user_profile != user_profile:
            items_qs = WishlistItem.objects.filter(wishlist=wishlist, is_public=True).order_by('-priority')
            data['items'] = WishlistItemSerializer(items_qs, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Only wishlist owner can delete"""
        wishlist = get_object_or_404(Wishlist, wishlist_id=self.kwargs.get('wishlist_id'))
        user_profile = request.user.userprofile
        if wishlist.user_profile != user_profile:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the wishlist owner can delete this wishlist.')

        wishlist.delete()
        return Response(
            {"message": "Wishlist deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class WishlistItemListCreateAPIView(APIView):
    """
    API endpoint for listing and creating wishlist items.
    GET /wishlists/<wishlist_id>/items - Returns all items in a wishlist
    POST /wishlists/<wishlist_id>/items - Adds a new item to the wishlist
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, wishlist_id, *args, **kwargs):
        """Return all items in the wishlist"""
        user_profile = request.user.userprofile

        # Get wishlist and verify ownership
        wishlist = get_object_or_404(
            Wishlist,
            wishlist_id=wishlist_id,
            user_profile=user_profile
        )

        items = WishlistItem.objects.filter(wishlist=wishlist)
        serializer = WishlistItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, wishlist_id, *args, **kwargs):
        """Add a new item to the wishlist"""
        user_profile = request.user.userprofile

        # Get wishlist and verify ownership
        wishlist = get_object_or_404(
            Wishlist,
            wishlist_id=wishlist_id,
            user_profile=user_profile
        )

        serializer = CreateUpdateWishlistItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the item
        item = WishlistItem.objects.create(
            wishlist=wishlist,
            **serializer.validated_data
        )

        response_serializer = WishlistItemSerializer(item)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class WishlistItemDetailAPIView(APIView):
    """
    API endpoint for retrieving, updating, and deleting a wishlist item.
    GET /wishlists/<wishlist_id>/items/<item_id> - Returns item details
    PUT /wishlists/<wishlist_id>/items/<item_id> - Updates item (only owner)
    PATCH /wishlists/<wishlist_id>/items/<item_id> - Partially updates item (only owner)
    DELETE /wishlists/<wishlist_id>/items/<item_id> - Deletes item (only owner)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_item_with_ownership_check(self, request, wishlist_id, item_id):
        """Helper method to get item and verify ownership"""
        user_profile = request.user.userprofile

        # Verify wishlist ownership
        wishlist = get_object_or_404(
            Wishlist,
            wishlist_id=wishlist_id,
            user_profile=user_profile
        )

        # Get the item
        item = get_object_or_404(
            WishlistItem,
            item_id=item_id,
            wishlist=wishlist
        )

        return item

    def get(self, request, wishlist_id, item_id, *args, **kwargs):
        """Return item details"""
        item = self.get_item_with_ownership_check(
            request, wishlist_id, item_id)
        serializer = WishlistItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, wishlist_id, item_id, *args, **kwargs):
        """Update item completely"""
        item = self.get_item_with_ownership_check(
            request, wishlist_id, item_id)

        serializer = CreateUpdateWishlistItemSerializer(
            item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = WishlistItemSerializer(item)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, wishlist_id, item_id, *args, **kwargs):
        """Delete item"""
        item = self.get_item_with_ownership_check(
            request, wishlist_id, item_id)
        item.delete()

        return Response(
            {"message": "Item deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class PickPingAPIView(APIView):
    """API endpoint to send a ping email to the picked user for a given pick.

    POST /wishlists/pick/<pick_id>/ping/ - Sends ping email to the picked user's email
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pick_id, *args, **kwargs):
        try:
            pick = Pick.objects.get(pick_id=pick_id)
        except Pick.DoesNotExist:
            return Response({"error": "Pick not found."}, status=status.HTTP_404_NOT_FOUND)

        # Verify requester is a member of the pick's group
        user_profile = request.user.userprofile
        if not GroupMember.objects.filter(group_id=pick.group_id, user_profile_id=user_profile).exists():
            return Response({"error": "You are not a member of this group."}, status=status.HTTP_403_FORBIDDEN)

        # Ensure picked profile and email exist
        if not getattr(pick, 'picked_profile', None):
            return Response({"error": "No picked profile available for this pick."}, status=status.HTTP_400_BAD_REQUEST)

        picked_profile = pick.picked_profile
        email = None
        if getattr(picked_profile, 'user', None):
            email = getattr(picked_profile.user, 'email', None)

        if not email:
            return Response({"error": "Picked user has no email address."}, status=status.HTTP_400_BAD_REQUEST)

        mail_manager = MailManager(email)

        ping_type = None
        if isinstance(request.data, dict):
            ping_type = request.data.get('type')
        if not ping_type:
            ping_type = request.query_params.get('type')
        ping_type = (ping_type or 'wishlist').lower()

        if ping_type == 'wishlist':
            success = mail_manager.ping_user_wishlist(pick.group_id)
            success_msg = 'Ping (wishlist) sent successfully.'
            fail_msg = 'Ping (wishlist) failed. Please try again later.'
        elif ping_type == 'address':
            success = mail_manager.ping_user_address(pick.group_id)
            success_msg = 'Ping (address) sent successfully.'
            fail_msg = 'Ping (address) failed. Please try again later.'
        else:
            return Response({"error": "Invalid ping type. Use 'wishlist' or 'address'."}, status=status.HTTP_400_BAD_REQUEST)

        if success:
            return Response({"message": success_msg}, status=status.HTTP_200_OK)
        return Response({"error": fail_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Support GET for convenience (mirrors existing UI behavior)
    def get(self, request, pick_id, *args, **kwargs):
        return self.post(request, pick_id, *args, **kwargs)
