import random
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from .forms import LoginForm, RegistrationForm, ProgrammingLanguagesFormset, CommentForm, UserProfileForm, \
    ChangeProgrammingLanguagesFormset
from .models import Member, CodeSnippet, Comment

THRESHOLD = 5
MAX_SKIP = 4


def login(request):
    if request.user.is_authenticated():
        return redirect('core:home')

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

    return render(request, 'auth/login.html', context={
        'login_form': form
    })


def register(request):
    if request.user.is_authenticated():
        return redirect('core:home')

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        pls = ProgrammingLanguagesFormset(request.POST, instance=Member())
        if form.is_valid():
            new_member = form.save()
            pls = ProgrammingLanguagesFormset(request.POST, instance=new_member)
            if pls.is_valid():
                pls.save()
                return redirect('core:login')
            else:
                new_member.delete()
    else:
        form = RegistrationForm()
        pls = ProgrammingLanguagesFormset()

    return render(request, 'auth/register.html', context={
        'register_form': form,
        'programming_languages': pls
    })


def logout(request):
    auth_logout(request)
    return redirect('core:home')


def _get_sidebar_context(request):
    all_snippets = CodeSnippet.objects.order_by('?').all()[:10]
    if request.user.is_authenticated():
        # programming_languages = request.user.programming_languages.all()
        commentable_snippets = request.user.get_commentable_snippets_query_set().order_by('-date_time').all()[:10]
        understandable_snippets = request.user.get_understandable_snippets_query_set().order_by('-date_time').all()[:10]
    else:
        programming_languages = commentable_snippets = understandable_snippets = None

    return {
        'all_snippets': all_snippets,
        # 'programming_languages': programming_languages,
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
        context = {'language': language, 'finished': order != 1}
        context.update(_get_sidebar_context(request))
        return render_to_response('no_snippet.html', context=context)

    try:
        prev_comment = Comment.objects.get(user=request.user, snippet=snippet)
        comment_form = CommentForm(instance=prev_comment)
    except Comment.DoesNotExist:
        comment_form = CommentForm()

    context = {
        'snippet': snippet,
        'order': order + 1,
        'comment_form': comment_form,
        'next_url': '{}?order={}'.format(request.path, order + 2),
        'skips': request.session.get('skips', 0),
        'available_skips': MAX_SKIP - request.session.get('skips', 0)
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
        'comment_form': comment_form,
        'skips': request.session.get('skips', 0),
        'available_skips': MAX_SKIP - request.session.get('skips', 0)
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

    if 'skip' in request.POST:
        if request.session.get('skips', 0) < MAX_SKIP:
            comment = Comment()
            comment.snippet = snippet
            comment.user = request.user
            comment.skip = True
            comment.save()
            if 'skips' not in request.session:
                request.session['skips'] = 0
            request.session['skips'] += 1

            return redirect('core:random')
        else:
            return HttpResponseRedirect(reverse('core:random') + '?id=' + str(snippet.pk))
    elif comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.user = request.user
        comment.snippet = snippet
        comment.save()
        request.session['skips'] = 0
        return HttpResponseRedirect(request.POST.get('next', reverse('core:home')))
    else:
        return HttpResponseRedirect(reverse('core:random') + '?id=' + str(snippet.pk))


@login_required
def show_random_snippet(request):
    snippet = None
    if 'id' in request.GET:
        try:
            snippet = CodeSnippet.get(pk=request.GET['id'])
        except CodeSnippet.DoesNotExist:
            pass
    try:
        if not snippet:
            available_snippets = request.user.get_commentable_snippets_query_set().order_by('-date_time').all()
            better_snippets = list(filter(lambda snippet: snippet.n_comments < THRESHOLD, available_snippets))

            if len(better_snippets) == 0:
                better_snippets = available_snippets

            snippet = random.choice(better_snippets)

        context = {
            'snippet': snippet,
            'comment_form': CommentForm(),
            'next_url': reverse('core:random'),
            'skips': request.session.get('skips', 0),
            'available_skips': MAX_SKIP - request.session.get('skips', 0)
        }
        context.update(_get_sidebar_context(request))

        return render(request, 'snippet.html', context=context)
    except Exception as e:
        print(e)
        context = {'finished': True}
        context.update(_get_sidebar_context(request))
        return render(request, 'no_snippet.html', context=context)


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

    return render(request, 'auth/profile.html', context=context)
