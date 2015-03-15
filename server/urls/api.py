from django.conf.urls import patterns, url

from django_annotation.views import *

api_urlpatterns = patterns(
    '',
    url(r'^api/json/annotation/(?P<doc_id>\d+?)$',
        SentenceView.as_view(),
        name=SentenceView.view_name),

    url(r'^api/json/search/(?P<query>\d+?)$',
        SentenceView.as_view(),
        name=SentenceView.view_name),
    )
