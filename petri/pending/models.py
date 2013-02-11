from django.db import models
from django.contrib.auth.models import User

from petri.bulletin.models import Bulletin
from petri.bulletin.models import connect_bulletin_signals


class Pending(Bulletin):
    pass

connect_bulletin_signals(Pending)
