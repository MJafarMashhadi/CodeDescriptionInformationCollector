from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    # Examples:
    # url(r'^$', 'InformationCollector.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('core.urls', namespace='core')),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )