from django.conf import settings

from django import forms
from django.contrib.auth.models import User

from petri.common.utils.helpers import setattr_safe

from petri.bulletin.forms import BulletinForm

from petri.event.models import Event


class EventForm(BulletinForm):
    start = forms.DateTimeField()
    end = forms.DateTimeField(required=False)
    where = forms.CharField(max_length=settings.WHERE_MAX_LEN, min_length=settings.WHERE_MIN_LEN)

    def clean(self):
        if not self._errors:
            if self.cleaned_data['end'] and self.cleaned_data['start'] >= self.cleaned_data['end']:
                raise forms.ValidationError, "The end time cannot be before the start time."

        return self.cleaned_data

    def save(self, instance=None, commit=True):
        # no editing and no deleting
        event = instance or Event()
        
        setattr_safe(event, 'start', self.cleaned_data['start'])
        setattr_safe(event, 'end', self.cleaned_data['end'])
        setattr_safe(event, 'where', self.cleaned_data['where'])
        
        return super(EventForm, self).save(event, commit=commit)
