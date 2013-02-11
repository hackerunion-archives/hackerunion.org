from django.conf import settings

from django import forms
from django.contrib.auth.models import User

from petri.bulletin.forms import BulletinForm

from petri.pending.models import Pending


class PendingForm(BulletinForm):
    def save(self, commit=True):
        pending = Pending()
        self._request.chapter = self._request.user.get_profile().chapter

        return super(PendingForm, self).save(pending, commit=commit, permanent=True)
