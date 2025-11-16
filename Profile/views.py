from .serializers import (
    UserProfileSerializer,
    UpdateUserProfileSerializer,
)
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from .utils import GetUserProfile, GetUserWishList
from django.shortcuts import render
from django.contrib import messages
from Group.utils import GroupManager
from django.shortcuts import redirect
from Auth.utils import VerificationManager
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


@method_decorator(csrf_protect, name='dispatch')
class HomeView(LoginRequiredMixin, View):
    template_name = 'profile/home.html'

    def get(self, request):
        if request.user.is_staff:
            messages.error(
                request, 'You are not allowed profile home. Admins do not have a profile.')
            return redirect('admin:index')
        else:
            user_profile = GetUserProfile(request.user)
            group_profile = GroupManager(request.user)
            print(group_profile.user_group().count())
            context = {
                'user_profile': user_profile.get_profile(),
                'santa_greet': user_profile.get_santa_greet(),
                'user_group_count': group_profile.user_group().count(),
                'verified': VerificationManager(user_profile.get_profile()).check_user_verified(),
            }
            return render(request, self.template_name, context)


@method_decorator(csrf_protect, name='dispatch')
class UpdateProfileView(LoginRequiredMixin, View):
    template_name = 'profile/update-profile.html'
    form = None

    def get(self, request):
        if request.user.is_staff:
            messages.error(
                request, 'You are not allowed to update profile. Admins do not have a profile.')
            return redirect('admin:index')
        else:
            user_profile = GetUserProfile(request.user)
            context = {
                'user_profile': user_profile.get_profile(),
                'form': self.form,
            }
            return render(request, self.template_name, context)

    def post(self, request):
        post_form = self.form(request.POST)
        if post_form.is_valid():
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.save()
            user_profile = GetUserProfile(request.user)
            user_profile.update_profile(request.POST.get(
                'gender'), request.POST.get('address'))
            messages.success(
                request, 'You have successfully updated your profile.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid form.')
            return redirect('update_profile')


@method_decorator(csrf_protect, name='dispatch')
class WishListView(LoginRequiredMixin, View):
    template_name = 'profile/wishlist.html'

    def get(self, request):
        if request.user.is_staff:
            messages.error(
                request, 'You are not allowed to view wishlist. Admins do not have a wishlist.'
            )
            return redirect('admin:index')
        else:
            user_profile = GetUserProfile(request.user)
            user_wishlist = GetUserWishList(request.user)
            context = {
                'user_profile': user_profile.get_profile(),
                'wishlist': user_wishlist.get_wishlist(),
            }
            return render(request, self.template_name, context)


@method_decorator(csrf_protect, name='dispatch')
class AddWishListView(LoginRequiredMixin, View):
    template_name = 'profile/add-wishlist.html'

    def post(self, request):
        user_wishlist = GetUserWishList(request.user)
        if user_wishlist.add_wishlist(request.POST.get('name'), request.POST.get('link')):
            messages.success(
                request, 'You have successfully added an item to your wishlist.')
            return redirect('wishlist')
        else:
            messages.error(request, 'Invalid form.')
            return redirect('wishlist')


@method_decorator(csrf_protect, name='dispatch')
class EditWishListView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        user_wishlist = GetUserWishList(request.user)
        if user_wishlist.update_wishlist(item_id, request.POST.get('name'), request.POST.get('link')):
            messages.success(
                request, 'You have successfully updated an item in your wishlist.')
        else:
            messages.error(request, 'Invalid form.')
        return redirect('wishlist')


@method_decorator(csrf_protect, name='dispatch')
class DeleteWishListView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        user_wishlist = GetUserWishList(request.user)
        if user_wishlist.delete_wishlist(item_id):
            messages.success(
                request, 'You have successfully deleted an item from your wishlist.')
            return redirect('wishlist')
        else:
            messages.error(request, 'Invalid form.')
        return redirect('wishlist')


##############################
# API VIEWS
##############################


class UserProfileAPIView(APIView):
    """
    API endpoint for retrieving the authenticated user's profile.
    GET /api/profile/ - Returns the user's profile information
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return the authenticated user's profile"""
        user_profile = request.user.userprofile
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """Update the authenticated user's profile"""
        user_profile = request.user.userprofile
        serializer = UpdateUserProfileSerializer(
            user_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
