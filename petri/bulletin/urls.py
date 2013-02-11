from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('petri.bulletin.views',
    url(r'^(?P<bulletin>\d+)/comment/?$', r'add_comment'),
    url(r'^(?P<bulletin>\d+)/comment/delete/(?P<comment>\d+)/?$', r'delete_comment'),
    url(r'^(?P<bulletin>\d+)/promote/?$', r'promote_bulletin'),
    url(r'^(?P<bulletin>\d+)/follow/?$', r'follow_bulletin'),
    url(r'^(?P<bulletin>\d+)/?$', r'home'),
    url(r'^go/(?P<alias>[a-zA-Z0-9_-]+)(?:/(?P<index>\d+))?/?$', r'alias')
)
