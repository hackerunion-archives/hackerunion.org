from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from petri.bulletin.models import BulletinFeed
from petri.talk.models import TalkFeed

urlpatterns = patterns('',
    url(r'', include('petri.base.urls')),
    url(r'^pending/', include('petri.pending.urls')),
    url(r'^accounts/', include('petri.account.urls')),
    url(r'^notifications/', include('petri.synergy.urls')),
    url(r'^petition/?', include('petri.petition.urls')),
    url(r'^mail/', include('petri.mail.urls')),
    url(r'^admin/?', include(admin.site.urls)),
    url(r'^(?P<chapter>\w+)/posts/', include('petri.bulletin.urls')),
    url(r'^(?P<chapter>\w+)/talk/', include('petri.talk.urls')),
    url(r'^(?P<chapter>\w+)/event/', include('petri.event.urls')),
    url(r'^(?P<chapter>\w+)/lead/', include('petri.leadership.urls')),
    url(r'^(?P<chapter>\w+)/intro/', include('petri.introduction.urls')),
    url(r'^(?P<chapter>\w+)/members/', include('petri.members.urls')),
    url(r'^(?P<chapter>\w+)/projects/', include('petri.project.urls')),
    url(r'^(?P<chapter>\w+)/?', include('petri.chapter.urls'))
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
)

urlpatterns += patterns('',
    (r'^(?P<chapter_slug>\w+)/feeds/all/?$', BulletinFeed()),
    (r'^(?P<chapter_slug>\w+)/feeds/talk/?$', TalkFeed()),
)




if settings.LOCAL:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
