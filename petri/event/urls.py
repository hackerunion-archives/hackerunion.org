from django.conf.urls.defaults import *

urlpatterns = patterns('petri.event.views',
    url(r'^/?$', r'add_event'),
    url(r'^(?P<bulletin>\d+)/?$', r'edit_event'),
)
