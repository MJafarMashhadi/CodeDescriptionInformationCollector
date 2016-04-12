# coding=utf-8
import random
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response, redirect

from .forms import CodeSnippetSubmitForm
from .forms import CommentForm
from .models import CodeSnippet, Comment
from .views import _get_sidebar_context

THRESHOLD = 5
MAX_SKIP = 4


@login_required
def snippet_lang(request, language):
    order = int(request.GET.get('order', 1)) - 1
    try:
        snippet = CodeSnippet.objects.filter(language__name__iexact=language, approved=True).order_by(
            '-date_time').all()[
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

    is_double = snippet.n_comments < 3
    context = {
        'snippet': snippet,
        'is_double': is_double,
        'snippet_score': (2 * snippet.score) if is_double else snippet.score,
        'order': order + 1,
        'comment_form': comment_form,
        'next_url': '{}?order={}'.format(request.path, order + 2),
        'skips': request.session.get('skips', 0),
        'available_skips': MAX_SKIP - request.session.get('skips', 0)
    }
    context.update(_get_sidebar_context(request))

    return render(request, 'snippet.html', context=context)


@login_required
def show_snippet(request, language, name):
    snippet = get_object_or_404(CodeSnippet, name=name, language__name=language)

    try:
        prev_comment = Comment.objects.get(user=request.user, snippet=snippet)
        comment_form = CommentForm(instance=prev_comment)
    except Comment.DoesNotExist:
        comment_form = CommentForm()

    is_double = snippet.n_comments < 3
    context = {
        'snippet': snippet,
        'is_double': is_double,
        'snippet_score': (2 * snippet.score) if is_double else snippet.score,
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
    is_double = snippet.n_comments < 3
    try:
        comment_form = CommentForm(data=request.POST, instance=Comment.objects.get(snippet=snippet, user=request.user))
    except Comment.DoesNotExist:
        comment_form = CommentForm(data=request.POST)

    if 'skip' in request.POST:
        if request.session.get('skips', 0) < MAX_SKIP:
            Comment.objects.create(
                snippet=snippet,
                user=request.user,
                skip=True
            )
            request.user.earn_xp(-1, 'Skipped {}'.format(snippet.name))
            if 'skips' not in request.session:
                request.session['skips'] = 0
            request.session['skips'] += 1
            request.session['snippet_id'] = None

            return redirect('core:random')
        else:
            return redirect('core:random')
    elif comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.user = request.user
        comment.snippet = snippet
        comment.save()
        request.session['skips'] = 0
        if is_double:
            request.user.earn_xp(2 * snippet.score,
                                 'Summarized {} for the first time (Double score)'.format(snippet.name))
        else:
            request.user.earn_xp(snippet.score, 'Summarized {}'.format(snippet.name))

        request.session['snippet_id'] = None
        return HttpResponseRedirect(request.POST.get('next', reverse('core:home')))
    else:
        return redirect('core:random')




@login_required
def show_random_snippet(request):
    snippet = None
    last_snippet_id = request.session.get('snippet_id', None)
    if last_snippet_id:
        try:
            snippet = CodeSnippet.objects.get(pk=last_snippet_id)
        except CodeSnippet.DoesNotExist:
            pass
    try:
        if not snippet:
            if Comment.objects.filter(skip=False, test=False, user=request.user).count() < 2:
                snippet = request.user.get_commentable_snippets_query_set().order_by('score').all()[0]
            else:
                available_snippets = request.user.get_commentable_snippets_query_set().order_by('-date_time').all()
                better_snippets = list(filter(lambda snippet: snippet.n_comments < THRESHOLD, available_snippets))

                if len(better_snippets) == 0:
                    better_snippets = available_snippets
                snippet = random.choice(better_snippets)

            request.session['snippet_id'] = snippet.pk

    except Exception as e:
        print(e)
        context = {'finished': True}
        context.update(_get_sidebar_context(request))
        return render(request, 'no_snippet.html', context=context)
    else:
        if request.user.has_mystery_box():
            prizes = filter(lambda p: not request.user.got_mystery_box_before(p),
                            ['nill', 'badge', 'score', 'xppoints'])
            prize = random.choice(list(prizes))
            {
                'nill': lambda: None,
                'badge': lambda: request.user.earn_badge('comp_eng'),
                'score': lambda: None,
                'xppoints': lambda: request.user.earn_xp(10, 'Earned in a mystery box :-)')
            }[prize]()
            request.user.add_mystery_box_to_history(prize)
            request.user.remove_mystery_box()
            mystery_box = prize
        else:
            mystery_box = None

        is_double = snippet.n_comments < 3
        context = {
            'snippet': snippet,
            'is_double': is_double,
            'snippet_score': (2 * snippet.score) if is_double else snippet.score,
            'comment_form': CommentForm(),
            'next_url': reverse('core:random'),
            'skips': request.session.get('skips', 0),
            'mystery_box': mystery_box,
            'available_skips': MAX_SKIP - request.session.get('skips', 0)
        }
        context.update(_get_sidebar_context(request))

        return render(request, 'snippet.html', context=context)



@login_required
def submit_new_snippet(request):
    if not request.user.can_submit_code():
        raise Http404()
    saved = False
    if request.method == 'POST':
        form = CodeSnippetSubmitForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.approved = False
            snippet.submitter = request.user
            snippet.save()

            count = CodeSnippet.objects.filter(submitter=request.user).count()
            if count == 1:
                request.user.earn_badge('code_submitter')
            elif count == 3:
                request.user.earn_badge('code_submitter_2')
            elif count == 4:
                request.user.earn_badge('code_submitter_3')

            saved = True
    else:
        form = CodeSnippetSubmitForm()

    context = {
        'form': form,
        'saved': saved,
    }

    context.update(_get_sidebar_context(request))

    return render(request, 'submit_snippet.html', context=context)
