from django.conf.urls.defaults import *

urlpatterns = patterns('petri.talk.views',
    url(r'^/?$', r'add_talk'),
    url(r'^(?P<bulletin>\d+)/?$', r'edit_talk'),
)
