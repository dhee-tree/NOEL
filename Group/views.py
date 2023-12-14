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
        except ObjectDoesNotExist:
            messages.error(request, 'Group does not exist.')
            return redirect('group_home')

        if group_profile.check_group_creator(group):
            context = {
                'group': group,
                'user_profile': user_profile.get_profile(),
            }
            return render(request, self.template_name, context)
        else:
            messages.error(request, f'You are not the owner {group}.')
            return redirect('group_home')

    def post(self, request, group_name):
        pass