from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            messages.error(request, 'You are not allowed profile home. Admins do not have a profile.')
            return redirect('admin:index')
        else:
            return redirect('home')
    else:
        return render(request, 'index.html')


class AboutView(TemplateView):
    template_name = 'about.html'

class ContactView(TemplateView):
    template_name = 'contact.html'

class PrivacyView(TemplateView):
    template_name = 'privacy.html'

class TermsView(TemplateView):
    template_name = 'terms.html'

class FAQView(TemplateView):
    template_name = 'faq.html'
