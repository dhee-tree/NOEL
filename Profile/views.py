from django.views import View
from .utils import GetUserProfile
from Group.utils import GroupManager
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
@method_decorator(csrf_protect, name='dispatch')
class HomeView(LoginRequiredMixin, View):
    template_name = 'profile/home.html'

    def get(self, request):
        if request.user.is_staff:
            messages.error(request, 'You are not allowed profile home. Admins do not have a profile.')
            return redirect('admin:index')
        else:
            user_profile = GetUserProfile(request.user)
            group_profile = GroupManager(request.user)
            context = {
                'user_profile': user_profile.get_profile(), 
                'santa_greet': user_profile.get_santa_greet(),
                'user_group_count': group_profile.user_group().count(),
            }
            return render(request, self.template_name, context)
        
    def post(self, request):
        group_code = request.POST.get('group_code').upper()
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
class UpdateProfileView(LoginRequiredMixin, View):
    template_name = 'profile/update-profile.html'
    form = None

    def get(self, request):
        if request.user.is_staff:
            messages.error(request, 'You are not allowed to update profile. Admins do not have a profile.')
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
            user_profile.update_profile(request.POST.get('gender'), request.POST.get('address'))
            messages.success(request, 'You have successfully updated your profile.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid form.')
            return redirect('update_profile')
