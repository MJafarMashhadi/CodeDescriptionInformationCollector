# coding=utf-8
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render

from core.models import ProgrammingLanguage
from .forms import RegistrationForm, ProgrammingLanguagesFormset, ICAuthenticationForm


def login(request):
    if request.user.is_authenticated():
        return redirect('core:home')

    if request.method == 'POST':
        form = ICAuthenticationForm(data=request.POST)
        if form.is_valid():
            redirect_url = request.GET.get('next', reverse('core:home'))
            if request.POST.get('remember', None):
                request.session.set_expiry(0)
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redirect_url)
    else:
        form = ICAuthenticationForm()

    return render(request, 'auth/login.html', context={
        'login_form': form
    })


def register(request):
    if request.user.is_authenticated():
        return redirect('core:home')

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        pls = ProgrammingLanguagesFormset(request.POST)
        if form.is_valid():
            new_member = form.save()
            pls = ProgrammingLanguagesFormset(request.POST)
            if pls.is_valid():
                for form in pls:
                    form.instance.user = new_member
                    form.save()
                return redirect('core:login')
            else:
                new_member.delete()
    else:
        form = RegistrationForm()
        programming_languages = [{'language': item.pk, 'proficiency': 0} for item in ProgrammingLanguage.objects.all()]
        pls = ProgrammingLanguagesFormset(initial=programming_languages)

    return render(request, 'auth/register.html', context={
        'register_form': form,
        'programming_languages': pls
    })


def logout(request):
    auth_logout(request)
    return redirect('core:home')
