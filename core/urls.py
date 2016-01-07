from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'InformationCollector.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^auth/login/$', 'core.views.login', name='login'),
    url(r'^auth/register/$', 'core.views.register', name='register'),
    url(r'^/?$', 'core.views.home', name='home'),
]
