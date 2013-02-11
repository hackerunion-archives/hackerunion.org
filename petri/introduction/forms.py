from django.conf import settings

from django import forms
from django.contrib.auth.models import User

from petri.bulletin.forms import BulletinForm
from petri.introduction.models import Introduction


class IntroductionForm(BulletinForm):
    def save(self, instance=None, commit=True):
        return super(IntroductionForm, self).save(instance or Introduction(), commit=commit)
