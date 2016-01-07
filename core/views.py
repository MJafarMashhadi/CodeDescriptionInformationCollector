from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from .forms import LoginForm, RegistrationForm


def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            redirect_url = request.GET.get('next', reverse('core:home'))
            if request.POST.get('remember', None):
                request.session.set_expiry(0)
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redirect_url)
    else:
        form = LoginForm()

    return render(request, 'login.html', context={
        'login_form': form
    })


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('core:login'))
    else:
        form = RegistrationForm()

    return render(request, 'register.html', context={
        'register_form': form
    })

def home(request):
    pass
