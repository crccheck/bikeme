from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include('bikeme.apps.core.urls', namespace='bikeme')),

    url(r'^admin/', include(admin.site.urls)),
)
