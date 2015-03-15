from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),)

urlpatterns += patterns('', url(r'^alchemy/', include('alchemy_restful.urls',
                                              app_name="alchemy_restful")), )

urlpatterns += patterns('', url(r'^', include('alchemy_server.urls',
                                              app_name="alchemy_server")), )

# if settings.DEBUG:
#     import debug_toolbar
#
#     urlpatterns += patterns('',
#                             url(r'^__debug__/', include(debug_toolbar.urls)),)