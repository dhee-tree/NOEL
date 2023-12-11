from django.views import View
from .utils import GetUserProfile
from Group.utils import GroupManager
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
@method_decorator(csrf_protect, name='dispatch')
class HomeView(LoginRequiredMixin, View):
    template_name = 'profile/home.html'

    def get(self, request):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)
        context = {
            'user_profile': user_profile.get_profile(), 
            'santa_greet': user_profile.get_santa_greet(),
            'user_group_count': group_profile.user_group().count(),
            'wrapped': user_profile.get_wrapped(),
            }
        return render(request, self.template_name, context)
        
    def post(self, request):
        group_code = request.POST.get('group_code')
        group_profile = GroupManager(request.user)
        if group_profile.check_group_code(group_code):
            if group_profile.join_group(group_code):
                messages.success(
                    request, 'You have successfully joined the group.')
                return redirect('home')
            else:
                messages.error(
                    request, 'You are already a member of this group.')
                return redirect('home')
        else:
            messages.error(request, 'Invalid group code.')
            return redirect('home')


@method_decorator(csrf_protect, name='dispatch')
class WrappedView(LoginRequiredMixin, View):
    template_name = 'profile/wrapped.html'

    def get(self, request):
        user_profile = GetUserProfile(request.user)
        group_profile = GroupManager(request.user)
        if user_profile.get_wrapped():
            if group_profile.check_pick():
                return redirect('unwrapped')
            context = {
                'user_profile': user_profile.get_profile(),
                'range': range(1, len(group_profile.get_group_members_list()) + 1),
                'members_list': group_profile.get_group_members_list(),
            }
            return render(request, self.template_name, context)
        else:
            return redirect('unwrapped')

        
    def post(self, request):
        pass

@method_decorator(csrf_protect, name='dispatch')
class UnwrappedView(LoginRequiredMixin, View):
    template_name = 'profile/unwrap.html'

    def get(self, request):
        user_profile = GetUserProfile(request.user)
        context = {'picked': user_profile.get_picked()}
        return render(request, self.template_name, context)
        
    def post(self, request):
        user_profile = GetUserProfile(request.user)
        list_of_members = user_profile.get_group_members_list()
        user_profile.set_picked(list_of_members[int(request.POST.get('pick')) - 1])
        user_profile.set_wrapped()
        context = {}
        return redirect('unwrapped')
