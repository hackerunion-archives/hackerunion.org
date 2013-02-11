from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('petri.project.views',
    url(r'^/?$', 'projects'),
    url(r'^(?P<bulletin>\d+)/?$', r'edit_project')
)
