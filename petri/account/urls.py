from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('petri.account.views',
    url(r'^apply/?$', r'apply', name="apply"),
    url(r'^apply/(?P<invite>\w+)/?$', r'apply', name="apply_invite"),
    url(r'^pending/?$', r'pending', name="pending"),
    url(r'^invite/?$', r'invite', name="invite"),
    url(r'^message/?$', r'message', name="message"),

    # these should be migrated to chapter when we refactor
    url(r'^abandon/?$', r'abandon', name="abandon"),
    url(r'^ban/?$', r'ban', name="ban"),
    url(r'^moderator/?$', r'moderator', name="moderator"),
    url(r'^guide/?$', r'guide', name="guide"),
    url(r'^markup/?$', r'markup', name="markup"),
    url(r'^transfer/?$', r'transfer', name="transfer"),

    url(r'^settings/notice/?$', r'settings_notice', name="settings_notice"),
    url(r'^settings/email/?$', r'settings_email', name="settings_email"),
    url(r'^settings/social/?$', r'settings_social', name="settings_social"),
    url(r'^settings/skill/?$', r'settings_skill', name="settings_skill"),
    url(r'^settings/resign/?$', r'settings_resign', name="settings_resign"),
    url(r'^settings/?$', r'settings', name="settings"),

    url(r'^guide/?$', r'guide', name="guide"),
    url(r'^reset-thanks/$', r'reset_thanks', name="reset_thanks"),
)

urlpatterns += patterns('',
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^login/$', 'django.contrib.auth.views.login', {"template_name": "account/login.jade"}),
    (r'^reset/$', 'django.contrib.auth.views.password_reset', {"template_name": "account/reset.jade", "post_reset_redirect": "/accounts/reset-thanks/"}),
    (r'^confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {"template_name": "account/confirm.jade", 'post_reset_redirect': '/accounts/login/'}),
    (r'^change/$', 'django.contrib.auth.views.password_change', {"template_name": "account/change.jade", "post_change_redirect": "/"}),
)
