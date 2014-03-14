from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.Landing.as_view(), name='home'),
    url(r'^(?P<slug>[\w\-]+)/$', views.MarketDetail.as_view(),
            name='market_detail'),
)
