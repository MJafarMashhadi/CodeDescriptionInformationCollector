# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from core.models import ProgrammingLanguage
from .forms import UserProfileForm, ProgrammingLanguagesFormset
from .models import Member, UserKnowsPL


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