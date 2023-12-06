from django.views import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .utils import GetUserProfile

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

class UnwrappedView(View):
    template_name = 'profile/unwrap.html'

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)
        
    def post(self, request):
        picked = request.POST.get('pick')
        context = {}
        return render(request, self.template_name, context)