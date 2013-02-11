from django.conf.urls.defaults import *

urlpatterns = patterns('petri.petition.views',
    url(r'^/?$', r'home'),
    url(r'^thanks/?$', r'thanks'),
)
