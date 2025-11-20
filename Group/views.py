import random
from .forms import createGroup
from .utils import GroupManager
from django.contrib import messages
from django.urls import reverse_lazy
from Profile.utils import GetUserProfile
from .models import SantaGroup, GroupMember
from django.shortcuts import render, redirect
from django.views.generic.edit import DeletionMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View, DeleteView
from Auth.utils import VerificationManager
from Profile.utils import GetUserWishList

# API imports
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SantaGroupSerializer, CreateGroupSerializer, UpdateGroupSerializer, JoinGroupSerializer

# Create your views here.
@method_decorator(csrf_protect, name='dispatch')
class HomeView(LoginRequiredMixin, View):
    template_name = 'group/group-home.html'

    def get(self, request):
        verified = VerificationManager(GetUserProfile(request.user).get_profile()).check_user_verified()
        if verified:
            context = {
                'groups': GroupManager(request.user).user_group(),
            }

            return render(request, self.template_name, context)
        else:
            messages.error(request, 'You need to verify your account to view groups.')
            return redirect('home')


@method_decorator(csrf_protect, name='dispatch')
class CreateGroupView(LoginRequiredMixin, View):
    form = None
    template_name = 'group/create.html'

    def get(self, request):
        verified = VerificationManager(GetUserProfile(request.user).get_profile()).check_user_verified()
        if verified:
            context = {
                'form': self.form,
            }
            return render(request, self.template_name, context)
        else:
            messages.error(request, 'You need to verify your account to create a group.')
            return redirect('home')

    def post(self, request):
        group_name = request.POST.get('group_name')
        group_manager = GroupManager(self.request.user)
        if group_manager.create_group(group_name):
            messages.success(request, 'Group created successfully!')
            messages.success(request, 'You can now invite your friends.')
            return redirect('group_home')
        else:
            messages.error(request, f'{group_name} already exists.')
            return redirect('group_create')


@method_decorator(csrf_protect, name='dispatch')
class JoinGroupView(LoginRequiredMixin, View):
    def post(self, request):
        group_code = request.POST.get('group_code').upper()
        group_profile = GroupManager(request.user)
        verified = VerificationManager(GetUserProfile(request.user).get_profile()).check_user_verified()
        if verified:
            if group_profile.check_group_code(group_code):
                group = SantaGroup.objects.get(group_code=group_code)
                if group_profile.check_group_member(group):
                    messages.error(request, 'You are already a member of this group.')
                    return redirect('group_home')
                else:
                    if group_profile.join_group(group_code):
                            messages.success(request, 'You have successfully joined the group.')
                            return redirect('group_home')
                    else:
                        messages.error(request, 'This group has been closed by the owner.')
                        return redirect('group_home')
            else:
                messages.error(request, 'Invalid group code.')
                if verified:
                    return redirect('group_home')
                else:
                    return redirect('home')
        else:
            messages.error(request, 'You need to verify your account to join a group.')
            return redirect('home')


@method_decorator(csrf_protect, name='dispatch')
class ViewGroupView(LoginRequiredMixin, View):
    template_name = 'group/view.html'

    def get(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        if group_profile.check_group_member(group):
            members = GroupMember.objects.filter(group_id=group)
            context = {
                'group': group,
                'members': members,
                'user_profile': user_profile.get_profile(),
                'group_owner': group_profile.check_group_creator(group),
                'is_open': group_profile.get_is_open(group),
                'wrapped': group_profile.get_wrapped(group),
            }

            return render(request, self.template_name, context)
        else:
            messages.error(request, f'You are not a member of {group_name}.')
            return redirect('group_home')
            
    def post(self, request, group_name):
        group_check_box = request.POST.get('group_check_box')
        group = SantaGroup.objects.get(group_name=group_name)
        group_manager = GroupManager(request.user)
        if group_check_box:
            group_manager.set_is_open(group, True)
            messages.success(request, 'Group is now open.')
            return redirect('group_view', group_name=group_name)
        else:
            group_manager.set_is_open(group, False)
            messages.success(request, 'Group is now closed.')
            return redirect('group_view', group_name=group_name)


@method_decorator(csrf_protect, name='dispatch')
class WrappedView(LoginRequiredMixin, View):
    template_name = 'group/wrapped.html'

    def get(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        if group_profile.get_wrapped(group):
            if group_profile.get_group_members_list(group) == []:
                messages.error(request, 'You are the only one on this group, invite your friends.')
                return redirect('group_view', group_name=group_name)
            else:
                if not group_profile.get_is_open(group):
                    if group_profile.check_pick(group):
                        messages.error(request, f'You already picked a user for {group}.')
                        return redirect('group_home')
                    else:
                        context = {
                            'user_profile': user_profile.get_profile(),
                            'range': range(1, GroupMember.objects.filter(group_id=group).count()),
                            'group': group,
                            'members_list': group_profile.get_group_members_list(group),
                            'group_status': group_profile.get_is_open(group),
                        }
                        return render(request, self.template_name, context)
                else:
                    messages.error(request, f'You cannot open your wrapped for {group}, it is still open.')
                    return redirect('group_view', group_name=group_name)
        else:
            messages.error(request, f'You have already opened your for {group}.')
            return redirect('group_home')

    def post(self, request):
        pass


@method_decorator(csrf_protect, name='dispatch')
class UnwrappedView(LoginRequiredMixin, View):
    template_name = 'group/unwrap.html'

    def get(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        if not group_profile.get_wrapped(group):
            if group_profile.get_group_members_list(group) == []:
                messages.error(request, 'You are the only one on this group, invite your friends.')
                return redirect('group_view', group_name=group_name)
            else:
                if not group_profile.get_is_open(group):
                    if group_profile.check_pick(group):
                        context = {
                            'user_profile': user_profile.get_profile(),
                            'group': group,
                            'picked': group_profile.get_picked(group),
                            'picked_address': group_profile.get_picked_address(group),
                            'picked_email': group_profile.get_picked_email(group),
                            'picked_wish_list': group_profile.get_picked_user_wishlist(group)
                        }
                        return render(request, self.template_name, context)
                    else:
                        messages.error(request, f'You have not picked a user for {group}.')
                        return redirect('group_home')
                else:
                    messages.error(request, f'You cannot open your wrapped for {group}, it is still open.')
                    return redirect('group_view', group_name=group_name)
        else:
            messages.error(request, f'You have not opened your wrap for {group}.')
            return redirect('group_home')

    def post(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        list_of_members = group_profile.get_group_members_list(group)
        random.shuffle(list_of_members)
        random.shuffle(list_of_members)
        random.shuffle(list_of_members)
        picked = request.POST.get('pick')
        if picked == None:
            messages.error(request, 'You did not pick a user.')
            return redirect('group_view', group_name=group_name)
        else:
            if not group_profile.get_is_open(group):
                if group_profile.check_pick(group):
                    messages.error(request, 'You already picked a user.')
                    group_member = GroupMember.objects.get(group_id=group, user_profile_id=user_profile.get_profile())
                    group_member.is_wrapped = False
                    group_member.save()
                    return redirect('group_view', group_name=group_name)
                else:
                    participant_picked = list_of_members[int(picked) - 1]
                    group_profile.set_picked(group, participant_picked)
                    group_member = GroupMember.objects.get(group_id=group, user_profile_id=user_profile.get_profile())
                    group_member.is_wrapped = False
                    group_member.save()

                    messages.success(request, f'You have successfully picked {participant_picked} for {group}.')
                    return redirect('group_view', group_name=group_name)
            else:
                messages.error(request, f'You cannot pick a user for {group}, it is open.')
                return redirect('group_view', group_name=group_name)


class LeaveGroupView(LoginRequiredMixin, View):
    def get(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        if group_profile.check_group_member(group):
            group_member = GroupMember.objects.get(group_id=group, user_profile_id=user_profile.get_profile())
            group_member.delete()
            messages.success(request, f'You have left {group}.')
            return redirect('group_home')
        else:
            messages.error(request, f'You are not a member of {group}.')
            return redirect('group_home')


@method_decorator(csrf_protect, name='dispatch')
class EditGroupView(LoginRequiredMixin, View):
    def post(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        if group_profile.check_group_creator(group):
            group.group_name = request.POST.get('group_name')
            group.save()
            messages.success(request, f'{group} edited successfully!')
            return redirect('group_home')
        else:
            messages.error(request, f'You are not the owner {group}.')
            return redirect('group_home')


@method_decorator(csrf_protect, name='dispatch')
class EditGroupStatusView(LoginRequiredMixin, View):
    def post(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)
        group = SantaGroup.objects.get(group_name=group_name)

        if group_profile.check_group_creator(group):
            group_status = request.POST.get('group_status')
            group_profile.set_is_open(group, group_status)
            if group_status == 'True':
                messages.success(request, f'{group} is now open.')
            else:
                messages.success(request, f'{group} is now closed.')
            return redirect('group_view', group_name=group_name)
        else:
            messages.error(request, f'You are not the owner {group}.')
            return redirect('group_home')


class DeleteGroupView(LoginRequiredMixin, DeletionMixin, View):
    model = SantaGroup
    template_name = 'group/delete.html'
    success_url = reverse_lazy('/group/home/')

    def get(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        if group_profile.check_group_creator(group):
            group.delete()
            messages.success(request, f'{group} deleted successfully!')
            return redirect('group_home')
        else:
            messages.error(request, f'You are not the owner {group}.')
            return redirect('group_home')


class InviteFriendsView(LoginRequiredMixin, View):
    template_name = 'group/group-invite.html'

    def get(self, request, group_name):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)

        try:
            group = SantaGroup.objects.get(group_name=group_name)
            context = {
                'group': group,
                'user_profile': user_profile.get_profile(),
            }
            return render(request, self.template_name, context)
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')


# ==================== API Views ====================

class GroupListCreateAPIView(APIView):
    """
    API endpoint for listing all user groups and creating a new group.
    GET /groups - Returns active and archived groups separately
    POST /groups - Creates a new group
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Return active and archived groups in separate arrays"""
        from django.db.models import Q
        
        user_profile = request.user.userprofile
        
        # Get all groups user is a member of OR created
        all_groups = SantaGroup.objects.filter(
            Q(groupmember__user_profile_id=user_profile) | 
            Q(created_by=user_profile)
        ).distinct()
        
        # Separate into active and archived
        active_groups = all_groups.filter(is_archived=False)
        archived_groups = all_groups.filter(is_archived=True)
        
        # Serialize both
        active_serializer = SantaGroupSerializer(active_groups, many=True)
        archived_serializer = SantaGroupSerializer(archived_groups, many=True)
        
        return Response({
            "active": active_serializer.data,
            "archived": archived_serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """Create a new group"""
        serializer = CreateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract validated data
        group_name = serializer.validated_data['group_name']
        
        # Use GroupManager to create the basic group (handles group_code generation)
        group_manager = GroupManager(request.user)
        
        if group_manager.create_group(group_name):
            # Get the created group and update it with all the additional fields
            group = SantaGroup.objects.get(group_name=group_name, created_by=request.user.userprofile)
            
            # Update all additional fields from validated data
            for field, value in serializer.validated_data.items():
                if field != 'group_name':  # Skip group_name as it's already set
                    setattr(group, field, value)
            group.save()
            
            response_serializer = SantaGroupSerializer(group)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "A group with this name already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )


class GroupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a specific group.
    GET /groups/<id> - Returns group details (active or archived)
    PUT /groups/<id> - Updates group (only owner can update)
    DELETE /groups/<id> - Deletes group (only owner can delete)
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'group_id'
    
    def get_queryset(self):
        """Return groups where the user is a member or created (including archived)"""
        from django.db.models import Q
        
        user_profile = self.request.user.userprofile
        return SantaGroup.objects.filter(
            Q(groupmember__user_profile_id=user_profile) | 
            Q(created_by=user_profile)
        ).distinct()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateGroupSerializer
        return SantaGroupSerializer
    
    def update(self, request, *args, **kwargs):
        """Only group creator can update the group"""
        group = self.get_object()
        group_manager = GroupManager(request.user)
        
        if not group_manager.check_group_creator(group):
            return Response(
                {"error": "Only the group creator can update this group."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if group.is_archived:
            return Response(
                {"error": "Cannot update an archived group. Please unarchive it first."},
                status=status.HTTP_423_LOCKED
            )
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(group, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_serializer = SantaGroupSerializer(group)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Only group creator can delete the group"""
        group = self.get_object()
        group_manager = GroupManager(request.user)
        
        if not group_manager.check_group_creator(group):
            return Response(
                {"error": "Only the group creator can delete this group."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        group.delete()
        return Response(
            {"message": "Group deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class JoinGroupAPIView(APIView):
    """
    API endpoint for joining a group using a group code.
    POST /groups/join - Join a group with a group code
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JoinGroupSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group_code = serializer.validated_data['group_code'].upper()
        group_manager = GroupManager(request.user)
        
        try:
            group = SantaGroup.objects.get(group_code=group_code)
        except SantaGroup.DoesNotExist:
            return Response(
                {"error": "Invalid group code."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is already a member
        if group_manager.check_group_member(group):
            return Response(
                {"error": "You are already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if group is open
        if not group.is_open:
            return Response(
                {"error": "This group has been closed by the owner."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Join the group using GroupManager
        if group_manager.join_group(group_code):
            response_serializer = SantaGroupSerializer(group)
            return Response(
                {
                    "message": "You have successfully joined the group.",
                    "group": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Unable to join the group."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ArchiveGroupAPIView(APIView):
    """
    API endpoint for archiving a group.
    POST /groups/<group_id>/archive - Archive a group (only owner)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, group_id, *args, **kwargs):
        try:
            group = SantaGroup.objects.get(group_id=group_id)
        except SantaGroup.DoesNotExist:
            return Response(
                {"error": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        group_manager = GroupManager(request.user)
        
        # Only group creator can archive
        if not group_manager.check_group_creator(group):
            return Response(
                {"error": "Only the group creator can archive this group."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Archive the group
        group.is_archived = True
        group.save()
        
        return Response(
            {"message": "Group archived successfully."},
            status=status.HTTP_200_OK
        )


class UnarchiveGroupAPIView(APIView):
    """
    API endpoint for unarchiving a group.
    POST /groups/<group_id>/unarchive - Unarchive a group (only owner)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, group_id, *args, **kwargs):
        try:
            group = SantaGroup.objects.get(group_id=group_id)
        except SantaGroup.DoesNotExist:
            return Response(
                {"error": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        group_manager = GroupManager(request.user)
        
        # Only group creator can unarchive
        if not group_manager.check_group_creator(group):
            return Response(
                {"error": "Only the group creator can unarchive this group."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Unarchive the group
        group.is_archived = False
        group.save()
        
        return Response(
            {"message": "Group unarchived successfully."},
            status=status.HTTP_200_OK
        )


class ToggleGroupStatusAPIView(APIView):
    """
    API endpoint for opening/closing a group.
    POST /groups/<group_id>/toggle-status - Toggle group open/close status (only owner)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, group_id, *args, **kwargs):
        try:
            group = SantaGroup.objects.get(group_id=group_id)
        except SantaGroup.DoesNotExist:
            return Response(
                {"error": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        group_manager = GroupManager(request.user)
        
        # Only group creator can toggle status
        if not group_manager.check_group_creator(group):
            return Response(
                {"error": "Only the group creator can change the group status."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if group.is_archived:
            return Response(
                {"error": "Cannot change status of an archived group. Please unarchive it first."},
                status=status.HTTP_423_LOCKED
            )
        
        # Toggle the status
        group.is_open = not group.is_open
        group.save()
        
        status_text = "opened" if group.is_open else "closed"
        
        response_serializer = SantaGroupSerializer(group)
        return Response(
            {
                "message": f"Group {status_text} successfully.",
                "group": response_serializer.data
            },
            status=status.HTTP_200_OK
        )


class LeaveGroupAPIView(APIView):
    """
    API endpoint for leaving a group.
    POST /groups/<group_id>/leave - Leave a group (any member)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, group_id, *args, **kwargs):
        try:
            group = SantaGroup.objects.get(group_id=group_id)
        except SantaGroup.DoesNotExist:
            return Response(
                {"error": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_profile = request.user.userprofile
        group_manager = GroupManager(request.user)
        
        # Check if user is a member
        if not group_manager.check_group_member(group):
            return Response(
                {"error": "You are not a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove the member
        try:
            group_member = GroupMember.objects.get(
                group_id=group, 
                user_profile_id=user_profile
            )
            group_member.delete()
            
            return Response(
                {"message": f"You have successfully left {group.group_name}."},
                status=status.HTTP_200_OK
            )
        except GroupMember.DoesNotExist:
            return Response(
                {"error": "Membership not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class CheckGroupOwnerAPIView(APIView):
    """
    API endpoint to check if the user is the creator/owner of a group.
    GET /groups/<group_id>/is-owner - Returns boolean indicating ownership
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, group_id, *args, **kwargs):
        try:
            group = SantaGroup.objects.get(group_id=group_id)
        except SantaGroup.DoesNotExist:
            return Response(
                {"error": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        group_manager = GroupManager(request.user)
        is_owner = group_manager.check_group_creator(group)
        
        return Response(
            {
                "is_owner": is_owner,
            },
            status=status.HTTP_200_OK
        )

