from django.conf.urls.defaults import *

urlpatterns = patterns('petri.pending.views',
    url(r'^/?$', r'add_pending'),
)
