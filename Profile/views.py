from django.views import View
from .utils import GetUserProfile
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

# Create your views here.
@method_decorator(login_required, name='dispatch')
class HomeView(View):
    template_name = 'profile/home.html'

    def get(self, request):
        user_profile = GetUserProfile(request.user)
        context = {
            'user_profile': user_profile.get_profile(), 
            'group_members_count': user_profile.group_members_count(),
            'santa_greet': user_profile.get_santa_greet(),
            'wrapped': user_profile.get_wrapped(),
            }
        return render(request, self.template_name, context)
        
    def post(self, request):
        pass

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class WrappedView(View):
    template_name = 'profile/wrapped.html'

    def get(self, request):
        user_profile = GetUserProfile(request.user)
        context = {
            'user_profile': user_profile.get_profile(),
            'range': range(1, len(user_profile.get_group_members_list()) + 1),
            'members_list': user_profile.get_group_members_list(),
        }
        return render(request, self.template_name, context)
        
    def post(self, request):
        pass

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class UnwrappedView(View):
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
        return render(request, self.template_name, context)