from django.conf.urls.defaults import *

urlpatterns = patterns('petri.introduction.views',
    url(r'^/?$', r'add_intro'),
    url(r'^(?P<bulletin>\d+)/?$', r'edit_intro'),
)
