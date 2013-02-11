from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('petri.base.views',
    url(r'^$', r'home'),
    url(r'^chapter/?$', r'chapters')
)
