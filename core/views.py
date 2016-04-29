# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from .models import Member

DOUBLE_LIMIT = 5

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
                                 .filter(n_comments_a__lt=DOUBLE_LIMIT) \
                                 .order_by('-score') \
                                 .all()[:10]
        normal_high_scores = request.user.get_commentable_snippets_query_set() \
                                 .annotate(n_comments_a=Count('usersViewed')) \
                                 .filter(n_comments_a__gte=DOUBLE_LIMIT) \
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
def leader_board(request):
    local = request.GET.get('local', '0') == '1'
    qs = Member.objects.order_by('-score')
    if local:
        exp = (request.user.experience / 6) * 6
        qs = qs.filter(experience__range=(exp, exp + 6))
        if request.user.is_staff:
            items = qs.all()
        else:
            items = qs[:3].all()
    else:
        if request.user.is_staff:
            items = qs.all()
        else:
            items = qs[:10*2].all()
    return render(request, 'leader_board.html', context={
        'items': items,
        'local': local,
    })


@login_required
def survey(request):
    return HttpResponseRedirect('https://docs.google.com/forms/d/11B3NPz4QOT-ooEsLg7hBP4Xf7ocefDES2dwZlANiC0g/viewform')


@login_required
def dont_show_survey_again(request):
    request.user.filled_survey = True
    request.user.save()

    return HttpResponse(status=200)


@login_required
def help(request):
    return render(request, 'help.html')
