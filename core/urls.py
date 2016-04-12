from django.conf.urls import url

urlpatterns = [
    # Examples:
    # url(r'^$', 'InformationCollector.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^auth/login/$', 'core.auth_views.login', name='login'),
    url(r'^auth/register/$', 'core.auth_views.register', name='register'),
    url(r'^auth/logout/$', 'core.auth_views.logout', name='logout'),
    url(r'^auth/profile/$', 'core.profile_views.profile', name='profile'),
    url(r'^\+(?P<username>[\w.-]{1,30})$', 'core.profile_views.user_profile', name='user_profile'),
    url(r'^snippet/language/(?P<language>[a-zA-Z0-9+-]+)/$', 'core.snippet_views.snippet_lang', name='snippet_by_language'),
    url(r'^snippet/(?P<language>[a-zA-Z0-9+-]+)/(?P<name>[a-zA-Z0-9 *+-_]+)/$', 'core.snippet_views.show_snippet',
        name='show_snippet'),
    url(r'^snippet/submit/$', 'core.snippet_views.submit_snippet', name='submit_snippet'),
    url(r'^snippet/$', 'core.snippet_views.show_random_snippet', name='random'),
    url(r'^evaluating/(?P<language>[a-zA-Z0-9+-]+)/(?P<name>[a-zA-Z0-9 *+-_]+)/$', 'core.evaluating_views.evaluating_snippet',
        name='evaluating_snippet'),
    url(r'^evaluating/$', 'core.evaluating_views.evaluating', name='evaluating'),
    url(r'^evaluating/comment/(?P<comment_id>\d+)$', 'core.evaluating_views.evaluating_comment', name='evaluating_comment'),
    url(r'^snippet/new$', 'core.snippet_views.submit_new_snippet', name='submit_code'),
    url(r'^leaderboard/$', 'core.views.leader_board', name='leaderboard'),
    url(r'^survey/$', 'core.views.survey', name='survey'),
    url(r'^survey/dont_show$', 'core.views.dont_show_survey_again', name='dont_show'),
    url(r'^help/$', 'core.views.help', name='help'),
    url(r'^/?$', 'core.views.home', name='home'),
]
