from .forms import createGroup
from .utils import GroupManager
from django.contrib import messages
from Profile.utils import GetUserProfile
from .models import SantaGroup, GroupMember
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, ListView, View

# Create your views here.
@method_decorator(csrf_protect, name='dispatch')
class HomeView(LoginRequiredMixin, View):
    template_name = 'group/group-home.html'

    def get(self, request):
        context = {
            'groups': GroupManager(request.user).user_group(),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        group_code = request.POST.get('group_code')
        group_profile = GroupManager(request.user)
        if group_profile.check_group_code(group_code):
            if group_profile.join_group(group_code):
                messages.success(request, 'You have successfully joined the group.')
                return redirect('group_home')
            else:
                messages.error(request, 'You are already a member of this group.')
                return redirect('group_home')
        else:
            messages.error(request, 'Invalid group code.')
            return redirect('group_home')


class CreateGroupView(LoginRequiredMixin, CreateView):
    model = SantaGroup
    form_class = createGroup
    template_name = 'group/create.html'
    success_url = '/group/home/'

    def form_valid(self, group):
        user_profile = GetUserProfile(self.request.user)
        group_manager = GroupManager(self.request.user)
        group.save()
        group_manager.create_group(group.instance)

        return super().form_valid(group)

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
            
        members = GroupMember.objects.filter(group_id=group)
        context = {
            'group': group,
            'members': members,
            'user_profile': user_profile.get_profile(),
            'group_owner': group_profile.check_group_creator(group),
            'is_open': group_profile.get_is_open(group),
        }

        return render(request, self.template_name, context)

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
