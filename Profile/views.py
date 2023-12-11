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
