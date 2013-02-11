from django.conf.urls.defaults import *

urlpatterns = patterns('petri.leadership.views',
    url(r'^join/?$', r'join_request'),
    url(r'^volunteer/?$', r'volunteer_request'),
    url(r'^resign/?$', r'resign'),
    url(r'^pair/?$', r'pair_request'),
    url(r'^help/?$', r'help_request'),
    url(r'^promote/?$', r'promote_request'),
    
    url(r'^(?P<bulletin>\d+)/cancel/?$', r'cancel'),

    # these URLs must map to the "human" version of each request type (in models.py)
    url(r'^(?P<bulletin>\d+)/join/?$', r'join_response'),
    url(r'^(?P<bulletin>\d+)/lead/?$', r'volunteer_response'),
    url(r'^(?P<bulletin>\d+)/pair/?$', r'pair_response'),
    url(r'^(?P<bulletin>\d+)/help/?$', r'help_response'),
    url(r'^(?P<bulletin>\d+)/promote/?$', r'promote_response')
)
