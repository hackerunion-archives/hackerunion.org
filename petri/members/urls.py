from django.conf.urls.defaults import *

urlpatterns = patterns('petri.members.views',
    url(r'^$', 'members'),
)