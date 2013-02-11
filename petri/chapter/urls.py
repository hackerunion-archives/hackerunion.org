from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('petri.chapter.views',
    url(r'^$', r'home'),
    url(r'^invite/?$', r'invite')
)
