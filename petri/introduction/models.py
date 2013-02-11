from django.conf import settings

from django.db import models

from petri.bulletin.models import Bulletin
from petri.bulletin.models import connect_bulletin_signals

class Introduction(Bulletin):
    pass


connect_bulletin_signals(Introduction)
