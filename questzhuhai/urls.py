from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^eleave/admin/', include(admin.site.urls)),
    url(r'^eleave/main/', include('maitenance.urls')),
    url(r'^eleave/leave/', include('leave.urls')),
	url(r'^eleave/$', "leave.views.leave_request"),
	url(r'^$', "leave.views.leave_request"),
)

import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
   )