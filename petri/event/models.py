from django.conf import settings

from django.db import models
from django.contrib.auth.models import User

from petri.bulletin.models import Bulletin
from petri.bulletin.models import connect_bulletin_signals


class Event(Bulletin):
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, default=None)
    where = models.CharField(max_length=settings.WHERE_MAX_LEN)


connect_bulletin_signals(Event)
