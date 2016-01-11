from django.shortcuts import render_to_response
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from .forms import LoginForm, RegistrationForm, ProgrammingLanguagesFormset, CommentForm, UserProfileForm, \
    ChangeProgrammingLanguagesFormset
from .models import Member, CodeSnippet, Comment


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


def _get_sidebar_context(request):
    all_snippets = CodeSnippet.objects.order_by('?').all()[:10]
    if request.user.is_authenticated():
        programming_languages = request.user.programming_languages.all()
        commentable_snippets = request.user.get_commentable_snippets_query_set().order_by('-date_time').all()[:10]
        understandable_snippets = request.user.get_understandable_snippets_query_set().order_by('-date_time').all()[:10]
    else:
        programming_languages = commentable_snippets = understandable_snippets = None

    return {
        'all_snippets': all_snippets,
        'programming_languages': programming_languages,
        'commentable_snippets': commentable_snippets,
        'understandable_snippets': understandable_snippets,
    }


def home(request):
    sidebar_context = _get_sidebar_context(request)
    return render(request, 'home.html', context=sidebar_context)


@login_required
def snippet_lang(request, language):
    order = int(request.GET.get('order', 1)) - 1
    try:
        snippet = CodeSnippet.objects.filter(language__name__iexact=language).order_by('-date_time').all()[
                  order:1 + order].get()
    except CodeSnippet.DoesNotExist:
        return render_to_response('no_snippet.html', context={'language': language, 'finished': order != 1})

    try:
        prev_comment = Comment.objects.get(user=request.user, snippet=snippet)
        comment_form = CommentForm(instance=prev_comment)
    except Comment.DoesNotExist:
        comment_form = CommentForm()

    context = {
        'snippet': snippet,
        'order': order + 1,
        'comment_form': comment_form,
        'next_url': '{}?order={}'.format(request.path, order + 2)
    }
    context.update(_get_sidebar_context(request))

    return render(request, 'snippet.html', context=context)


@login_required
def show_snippet(request, name):
    snippet = get_object_or_404(CodeSnippet, name=name)

    try:
        prev_comment = Comment.objects.get(user=request.user, snippet=snippet)
        comment_form = CommentForm(instance=prev_comment)
    except Comment.DoesNotExist:
        comment_form = CommentForm()

    context = {
        'snippet': snippet,
        'comment_form': comment_form
    }
    context.update(_get_sidebar_context(request))

    return render(request, 'snippet.html', context=context)


@login_required
def submit_snippet(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    snippet = get_object_or_404(CodeSnippet, pk=request.POST.get('snippet', None))
    try:
        comment_form = CommentForm(data=request.POST, instance=Comment.objects.get(snippet=snippet, user=request.user))
    except Comment.DoesNotExist:
        comment_form = CommentForm(data=request.POST)

    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.user = request.user
        comment.snippet = snippet
        comment.save()
        return HttpResponseRedirect(request.POST.get('next', reverse('core:home')))
    else:
        pass  # TODO: redirect back to form w/ validation errors


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, instance=request.user)
        pls = ChangeProgrammingLanguagesFormset(data=request.POST, instance=request.user)
        if form.is_valid() and pls.is_valid():
            form.save()
            pls.save()
    else:
        form = UserProfileForm(instance=request.user)
        pls = ChangeProgrammingLanguagesFormset(instance=request.user)

    context = {
        'profile_form': form,
        'programming_languages_from': pls
    }
    context.update(_get_sidebar_context(request))

    return render(request, 'profile.html', context=context)
