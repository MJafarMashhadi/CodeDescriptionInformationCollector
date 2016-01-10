from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from .forms import LoginForm, RegistrationForm, ProgrammingLanguagesFormset
from .models import Member, CodeSnippet


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('core:home'))

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
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('core:home'))

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        pls = ProgrammingLanguagesFormset(request.POST, instance=Member())
        if form.is_valid():
            new_member = form.save()
            pls = ProgrammingLanguagesFormset(request.POST, instance=new_member)
            if pls.is_valid():
                pls.save()
                return HttpResponseRedirect(reverse('core:login'))
            else:
                new_member.delete()
    else:
        form = RegistrationForm()
        pls = ProgrammingLanguagesFormset()

    return render(request, 'register.html', context={
        'register_form': form,
        'programming_languages': pls
    })


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core:home'))


def home(request):
    all_snippets = CodeSnippet.objects.all()
    if request.user.is_authenticated():
        programming_languages = request.user.programming_languages.all()
        commentable_snippets = request.user.get_commentable_snippets()
        understandable_snippets = request.user.get_understandable_snippets()
    else:
        programming_languages = commentable_snippets = understandable_snippets = None

    return render(request, 'home.html', context={
        'all_snippets': all_snippets,
        'programming_languages': programming_languages,
        'commentable_snippets': commentable_snippets,
        'understandable_snippets': understandable_snippets,
    })
