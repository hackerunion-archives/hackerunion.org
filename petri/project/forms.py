from django.conf import settings

from django import forms
from django.contrib.auth.models import User

from petri.project.models import Project
from petri.bulletin.forms import BulletinForm

class ProjectForm(BulletinForm):
    url = forms.URLField(required=False)

    def save(self, instance=None, commit=True):
        project = instance or Project()
        project.picture = self.cleaned_data['url']

        return super(ProjectForm, self).save(project, commit=commit)
