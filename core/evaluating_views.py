# coding=utf-8
import random
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum, Case, When, IntegerField, Q
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404

from core.models import Evaluate
from .models import Member, CodeSnippet, Comment


@login_required
def evaluating(request):
    if Comment.objects.filter(user=request.user, skip=False, test=False).count() < 10:
        return render(request, 'evaluating.html', context={
            'must_comment': True,
        })
    snippets = CodeSnippet.objects.all().annotate(
        comment__count=Sum(Case(When(comment__skip=False, comment__test=False, then=1), output_field=IntegerField()),
                           distinct=True)).filter(
        comment__count__gt=2).order_by('-comment__count')

    for snippet in snippets:
        evaluated_comments = Evaluate.objects.filter(user=request.user, comment__snippet=snippet) \
            .exclude(comment__user=request.user).count()
        this_user_comments = 1 if Comment.objects.filter(user=request.user, snippet=snippet, skip=False).exists() else 0
        snippet.real_comment_count = snippet.comment__count - (evaluated_comments + this_user_comments)

    snippets = sorted(snippets, key=lambda x: x.real_comment_count, reverse=True)[:5]

    context = {
        'must_comment': False,
        'snippets': snippets
    }

    return render(request, 'evaluating.html', context=context)


@login_required
def evaluating_snippet(request, language, name):
    snippet = get_object_or_404(CodeSnippet, name=name, language__name=language)
    if not Comment.objects.filter(snippet=snippet, user=request.user).exists():
        raise PermissionDenied

    evaluation_comments = list(set(list(Comment.objects.annotate(Count('evaluate', distinct=True))
                                        .filter(skip=False,
                                                test=False,
                                                snippet=snippet).
                                        exclude(
        Q(user=request.user) | Q(evaluate__user=request.user) | Q(evaluate__count__gt=5)).distinct()
                                        .order_by('?')[:5])))
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
                u"I don't know exactly...",
                u"It does something for sure",
                u"Give me some badges :-D",
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
