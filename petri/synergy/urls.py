from django.conf.urls.defaults import *

urlpatterns = patterns('petri.synergy.views',
    url(r'^read/?$', r'read'),
    url(r'^get/?$', r'get'),
)
