from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('petri.mail.views',
    url(r'^discuss/?$', r'discuss'),
    url(r'^official/?$', r'official')
)
