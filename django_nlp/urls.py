from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'django_nlp.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),)

urlpatterns += patterns('', url(r'^', include('django_annotation.urls',
                                              app_name="django_annotation")), )

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),)