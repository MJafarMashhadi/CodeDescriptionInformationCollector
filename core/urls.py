from django.conf.urls import url

urlpatterns = [
    # Examples:
    # url(r'^$', 'InformationCollector.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^auth/login/$', 'core.views.login', name='login'),
    url(r'^auth/register/$', 'core.views.register', name='register'),
    url(r'^auth/logout/$', 'core.views.logout', name='logout'),
    url(r'^auth/profile/$', 'core.views.profile', name='profile'),
    url(r'^\+(?P<username>[\w.-]{1,30})$', 'core.views.user_profile', name='user_profile'),
    url(r'^snippet/language/(?P<language>[a-zA-Z0-9+-]+)/$', 'core.views.snippet_lang', name='snippet_by_language'),
    url(r'^snippet/submit/$', 'core.views.submit_snippet', name='submit_snippet'),
    url(r'^snippet/(?P<name>[a-zA-Z0-9 *+-_]+)/$', 'core.views.show_snippet', name='show_snippet'),
    url(r'^snippet/$', 'core.views.show_random_snippet', name='random'),
    url(r'^leaderboard/$', 'core.views.leader_board', name='leaderboard'),
    url(r'^/?$', 'core.views.home', name='home'),
]
