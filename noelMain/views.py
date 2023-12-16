from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from Mail.utils import MailManager

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

class ContactView(View):
    template_name = 'contact.html'
    form = None

    def get(self, request):
        context = {
            'form': self.form
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        post_form = self.form(request.POST)
        if post_form.is_valid():
            name = post_form.cleaned_data['name']
            email = post_form.cleaned_data['email']
            message = post_form.cleaned_data['message']
            mail_manager = MailManager(email)
            mail_manager.send_contact_message(name, message)
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('contact')
        else:
            messages.error(request, 'Your message was not sent. Please try again.')
            return redirect('contact')

class PrivacyView(TemplateView):
    template_name = 'privacy.html'

class TermsView(TemplateView):
    template_name = 'terms.html'

class FAQView(TemplateView):
    template_name = 'faq.html'
