from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponse


admin.autodiscover()


def my_image(request):
    """Hack to serve a favicon."""
    image_data = open('bikeme/static/favicon.ico', 'rb').read()
    return HttpResponse(image_data, mimetype='image/png')


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^favicon.ico$', my_image),
    url(r'', include('bikeme.apps.core.urls', namespace='bikeme')),
)
