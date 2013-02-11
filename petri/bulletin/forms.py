from django.conf import settings

from django import forms
from django.contrib.auth.models import User

from petri.common.utils.forms import DeletionForm
from petri.common.utils.forms import SmartNullBooleanField

from petri.common.utils.helpers import setattr_safe

from petri.bulletin.models import Comment
from petri.bulletin.models import Bulletin

# IMPORTANT: all bulletin forms that accept a request parameter must also
# work with the bulletin.utils.BulletinRequest to support out-of-request
# operations.

class CommentForm(DeletionForm):
    content = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self._request = request

    def clean_content(self):
        content = self.cleaned_data['content'].strip()

        if not content:
            raise forms.ValidationError, "Your content cannot be blank"

        return content

    def save(self, instance=None, commit=True):
        # if we're editing, we assume that the user has already been confirmed as comment owner
        comment = instance or Comment()

        comment.owner = self._request.user
        comment.bulletin = self._request.bulletin
        comment.content = self.cleaned_data['content']

        if commit:
            if self.is_delete():
                comment.delete()
            else:
                comment.save()

        return comment


class PromoteForm(forms.Form):
    # toggles promoted status -- and may lead to auto-sharing/digesting
    def __init__(self, request, *args, **kwargs):
        super(PromoteForm, self).__init__(*args, **kwargs)

        self._request = request

    def save(self):
        from petri.leadership.utils import create_promote_request

        if self._request.user.get_profile().is_leader:
            if self._request.bulletin.is_promoted():
                self._request.bulletin.unpromote()
            else:
                self._request.bulletin.promote(self._request.user)

            return True

        create_promote_request(self._request.user, self._request.chapter, self._request.bulletin, request=self._request)

        return False


class FollowForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super(FollowForm, self).__init__(*args, **kwargs)
        self._request = request

    def save(self):
        if self._request.user in self._request.bulletin.followed_by.all():
            self._request.bulletin.unfollow(self._request.user)
            return False

        self._request.bulletin.follow(self._request.user)
        return True


class BulletinForm(DeletionForm):
    title = forms.CharField(max_length=settings.TITLE_MAX_LEN, required=False)
    content = forms.CharField()
    related = forms.ModelChoiceField(queryset=Bulletin.objects.all(), required=False)
    is_global = SmartNullBooleanField(required=False)
    is_official = SmartNullBooleanField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(BulletinForm, self).__init__(*args, **kwargs)
        self._request = request
    
    def clean_title(self):
        title = self.cleaned_data.get('title')

        if title:
            title = title.strip()

        return title

    def clean_content(self):
        content = self.cleaned_data['content'].strip()

        # if explicitly not required (i.e., this is a deletion request), don't bother here
        if not self.fields['content'].required:
            return content

        if not content:
            raise forms.ValidationError, "Your content cannot be blank"

        return content

    def clean_is_global(self):
        is_global = self.cleaned_data['is_global']

        if is_global and not self._request.user.get_profile().is_leader:
            raise forms.ValidationError, "Only leaders can post global bulletins."

        return is_global

    def clean_is_official(self):
        is_official = self.cleaned_data['is_official']

        if is_official and not self._request.user.get_profile().is_leader:
            raise forms.ValidationError, "Only leaders can post official bulletins."

        return is_official

    def get_request(self):
        return self._request

    def save(self, bulletin, commit=True, permanent=False):
        # must only be invoked by a subclass, where bulletin is a proper instance
        if hasattr(bulletin, 'owner'):
          if bulletin.owner != self._request.user:
            bulletin.moderated_by = self._request.user

        else:
          bulletin.owner = self._request.user
        
        if not hasattr(bulletin, 'chapter'):
          bulletin.chapter = self._request.chapter

        setattr_safe(bulletin, 'title', self.cleaned_data['title'])
        setattr_safe(bulletin, 'content', self.cleaned_data['content'])
        setattr_safe(bulletin, 'related', self.cleaned_data['related'])
        setattr_safe(bulletin, 'is_global', self.cleaned_data['is_global'])
        setattr_safe(bulletin, 'is_official', self.cleaned_data['is_official'])

        if commit:
            if self.is_delete() and not permanent:
                bulletin.delete()
            else:
                bulletin.save()
                bulletin.follow(self._request.user)

        return bulletin
