from django.conf import settings

from django import forms
from django.contrib.auth.models import User

from petri.common.utils.helpers import setattr_safe
from petri.common.utils.forms import SmartNullBooleanField

from petri.bulletin.forms import BulletinForm

from petri.talk.models import Talk


class TalkForm(BulletinForm):
    is_announcement = SmartNullBooleanField(required=False)

    def save(self, instance=None, commit=True):
        talk = instance or Talk()
        setattr_safe(talk, 'is_announcement', self.cleaned_data['is_announcement'])

        return super(TalkForm, self).save(talk, commit=commit)
