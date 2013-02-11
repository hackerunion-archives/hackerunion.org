from django.contrib import admin
from petri.synergy.models import Notification, NotificationType, NotificationDict

admin.site.register(Notification)
admin.site.register(NotificationType)
admin.site.register(NotificationDict)
