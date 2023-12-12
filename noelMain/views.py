from django.contrib import messages
from django.shortcuts import render, redirect

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