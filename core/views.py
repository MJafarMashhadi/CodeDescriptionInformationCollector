# coding=utf-8
import random
from django.core.exceptions import PermissionDenied
from core.models import ProgrammingLanguage, Evaluate
from django.db.models import Count, Sum, Case, When, IntegerField, Q
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from .forms import RegistrationForm, CommentForm, UserProfileForm, ProgrammingLanguagesFormset, CodeSnippetSubmitForm, ICAuthenticationForm
from .models import Member, CodeSnippet, Comment, UserKnowsPL

THRESHOLD = 5
MAX_SKIP = 4


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
            form.get_user().set_mystery_boxes()
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


def _get_sidebar_context(request):
    if request.user.is_authenticated():
        programming_languages = request.user.get_knwon_programming_languages().all()
        fewest_summaries = request.user.get_commentable_snippets_query_set() \
                               .annotate(n_comments_a=Count('usersViewed')) \
                               .filter(n_comments_a__gt=0) \
                               .order_by('n_comments_a') \
                               .all()[:10]

        if len(fewest_summaries) == 0:
            fewest_summaries = request.user.get_commentable_snippets_query_set().order_by('?').all()[:10]

        double_high_scores = request.user.get_commentable_snippets_query_set() \
                                 .annotate(n_comments_a=Count('usersViewed')) \
                                 .filter(n_comments_a__lt=3) \
                                 .order_by('-score') \
                                 .all()[:10]
        normal_high_scores = request.user.get_commentable_snippets_query_set() \
                                 .annotate(n_comments_a=Count('usersViewed')) \
                                 .filter(n_comments_a__gte=3) \
                                 .order_by('-score') \
                                 .all()[:10]

        all_high_scores = dict()

        for snippet in double_high_scores:
            all_high_scores[snippet] = 2 * snippet.score, True

        for snippet in normal_high_scores:
            all_high_scores[snippet] = snippet.score, False

        all_high_scores = sorted(all_high_scores.items(), key=lambda a: -a[1][0])[:10]

        return {
            'programming_languages': programming_languages,
            'fewest_summaries': fewest_summaries,
            'highest_scores': all_high_scores,
        }
    else:
        return dict()


def home(request):
    if request.user.is_authenticated() and not request.user.should_see_home():
        return redirect('core:random')
    sidebar_context = _get_sidebar_context(request)
    return render(request, 'home.html', context=sidebar_context)


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

            saved = True
    else:
        form = CodeSnippetSubmitForm()

    context = {
        'form': form,
        'saved': saved,
    }

    context.update(_get_sidebar_context(request))

    return render(request, 'submit_snippet.html', context=context)


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
            prizes = ['nill', 'badge', 'score', 'xppoints']
            for p in prizes:
                if request.user.got_mystery_box_before(p):
                    prizes.remove(p)
            prize = random.choice(prizes)
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
def evaluating(request):
    snippets = CodeSnippet.objects.all().annotate(
        comment__count=Sum(Case(When(comment__skip=False, comment__test=False, then=1), output_field=IntegerField()),
                           distinct=True)).filter(
        comment__count__gt=0).order_by('-comment__count')

    for snippet in snippets:
        evaluated_comments = Evaluate.objects.filter(user=request.user, comment__snippet=snippet) \
            .exclude(comment__user=request.user).count()
        this_user_comments = 1 if Comment.objects.filter(user=request.user, snippet=snippet, skip=False).exists() else 0
        snippet.real_comment_count = snippet.comment__count - (evaluated_comments + this_user_comments)

    snippets = sorted(snippets, key=lambda x: x.real_comment_count, reverse=True)[:5]

    context = {
        'snippets': snippets
    }

    return render(request, 'evaluating.html', context=context)


@login_required
def evaluating_snippet(request, language, name):
    snippet = get_object_or_404(CodeSnippet, name=name, language__name=language)

    evaluation_comments = list(Comment.objects.annotate(Count('evaluate', distinct=True)).filter(skip=False,
                                                                                                 test=False,
                                                                                                 snippet=snippet).
                               exclude(
        Q(user=request.user) | Q(evaluate__user=request.user) | Q(evaluate__count__gt=5)).distinct().order_by('?')[:5])
    if (not request.user.test_comment or random.randint(1, 4) == 3) and evaluation_comments:
        test_comment, is_new = Comment.objects.get_or_create(user=Member.objects.get(email="mmmdamin@gmail.com"),
                                                             test=True,
                                                             snippet=snippet,
                                                             )
        if is_new:
            test_comment.comment = random.choice([
                u"test! i'm sure",
                u"ممنون کد خوبی بود",
                u"What the code!",
                u"I don't know exactly..."
            ])
            test_comment.save()
        evaluation_comments[0] = test_comment
        if not request.user.test_comment:
            request.user.test_comment = True
            request.user.save()

    context = {
        'snippet': snippet,
        'evaluation_comments': evaluation_comments
    }
    return render(request, 'evaluating_snippet.html', context=context)


@login_required
def evaluating_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user or comment.skip:
        raise PermissionDenied
    evaluate, is_new = Evaluate.objects.get_or_create(comment=comment, user=request.user)
    evaluate.agree = request.POST.get('agree') == "true"
    xp_points = 1 if evaluate.agree else -1

    if is_new:
        request.user.earn_xp(1, 'evaluating a comment')
        xp_desc = 'for evaluation on your comment'
        xp = comment.user.earn_xp(xp_points, xp_desc)
    else:
        xp = evaluate.xp
        xp.amount = xp_points
        xp.save()

    evaluate.xp = xp
    evaluate.save()

    return JsonResponse({
        'agree': comment.agree_count,
        'disagree': comment.disagree_count,
    })


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, instance=request.user)
        pls = ProgrammingLanguagesFormset(data=request.POST)
        UserKnowsPL.objects.filter(user=request.user).delete()
        if form.is_valid() and pls.is_valid():
            form.save()
            user_pl = []
            for f in pls:
                f.instance.user = request.user
                user_pl.append(f.save(commit=False))
            UserKnowsPL.objects.bulk_create(user_pl)
    else:
        form = UserProfileForm(instance=request.user)
        user_proficiency = {}
        for item in UserKnowsPL.objects.filter(user=request.user):
            user_proficiency[item.language.pk] = item.proficiency

        programming_languages = [
            {
                'language': item.pk,
                'proficiency': 0 if item.pk not in user_proficiency else user_proficiency[item.pk]
            } for item in ProgrammingLanguage.objects.all()
            ]
        print(programming_languages)
        pls = ProgrammingLanguagesFormset(initial=programming_languages)

    context = {
        'profile_form': form,
        'programming_languages_form': pls
    }
    return render(request, 'auth/profile.html', context=context)


def user_profile(request, username):
    user = get_object_or_404(Member, username__iexact=username)
    xp_points_history = user.experiences.order_by('-date_time')[:5].all()
    return render(request, 'auth/user_profile.html', context={
        'user': user,
        'xp_points_history': xp_points_history,
    })


def leader_board(request):
    local = request.GET.get('local', '0') == '1'
    qs = Member.objects.order_by('-score')
    if local:
        exp = (request.user.experience / 6) * 6
        qs = qs.filter(experience__range=(exp, exp + 6))
        items = qs[:3].all()
    else:
        items = qs[:10].all()
    return render(request, 'leader_board.html', context={
        'items': items,
        'local': local,
    })


def survey(request):
    request.user.filled_survey = True
    request.user.save()

    return HttpResponseRedirect('https://docs.google.com/forms/d/11B3NPz4QOT-ooEsLg7hBP4Xf7ocefDES2dwZlANiC0g/viewform')


def help(request):
    return render(request, 'help.html')