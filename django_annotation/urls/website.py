from django.conf.urls import patterns, url

from django_annotation.views import *

web_urlpatterns = patterns(
    '',
    url(r'^$',IndexView.as_view(),name='index'),
    url(r'^contact$',ContactView.as_view(),name='contact'),
    url(r'^handle$',IndexView.as_view(),name='handle_search'),

    url(r'^search/(?P<query>(.|\n)+)$',
        SearchView.as_view(),
        name=SearchView.view_name),

    url(r'^download/(?P<query>(.|\n)+?)/(?P<dtype>.+?)$',
        DownloadView.as_view(),
        name=DownloadView.view_name),

    url(r'^annotation/(?P<doc_id>\d+)$',
        AnnotationView.as_view(),
        name=AnnotationView.view_name),

    url(r'^annotation/(?P<doc_id>\d+?)/(?P<rel_id>[0-9,]+)$',
        SentenceView.as_view(),
        name=SentenceView.view_name),

    url(r'^brat/(?P<doc_ids>.+?)$',
        BratView.as_view(),
        name=BratView.view_name),

    )
