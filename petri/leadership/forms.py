from django.conf import settings

from django import forms
from django.contrib.auth.models import User

from petri.bulletin.forms import BulletinForm

from petri.leadership.models import Leadership

#
# File requests
#

class CancelRequestForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super(self, CancelRequestForm).__init__(*args, **kwargs)
        self._request = request

    def clean(self):
        if not self._request.bulletin.can_cancel():
            raise forms.ValidationError, "This request cannot be canceled."

        if not self._request.bulletin.can_respond():
            raise forms.ValidationError, "This request is no longer active."

        return self.cleaned_data

    def save(self):
        self._request.bulletin.cancel()


class RequestForm(BulletinForm):
    # These do not rely on "bulletin" being bound in the request (but do require user and chapter)

    @classmethod
    def validate(cls, user, data=None, bulletin=None):
        return None

    def clean_is_official(self):
        return True

    def clean_title(self):
        return "%s wants to contact a leader." % (self._request.user.username)

    def clean(self):
        if not self._errors:
            if not getattr(self, "allow_multiple", False) and Leadership.objects.has_requested(self._request.user, self.request_type):
                raise forms.ValidationError, "User has already issued this request."

            message = self.validate(self._request.user, data=self.cleaned_data)

            if message is not None:
                raise forms.ValidationError, message

        return self.cleaned_data

    def save(self, instance=None, commit=True):
        leadership = instance or Leadership()
        leadership.request = self.request_type

        return super(RequestForm, self).save(leadership, commit=commit)


class PromoteRequestForm(RequestForm):
    request_type = Leadership.PROMOTE
    allow_multiple = True

    def clean_title(self):
        return "%s wants to endorse a post." % (self._request.user.username)

    def clean(self):
        self.cleaned_data = super(PromoteRequestForm, self).clean()

        if not self._errors:
            related = self.cleaned_data.get('related')

            if related is None:
                raise forms.ValidationError, "You must include a post to endorse in your request."

            if Leadership.objects.filter(request=Leadership.PROMOTE, related=related).exists():
                raise forms.ValidationError, "A user has already requested that this content be endorsed."

        return self.cleaned_data

    @classmethod
    def validate(self, user, data=None, bulletin=None):
        post = bulletin.related if data is None else data.get('related')

        if post is None:
            return "The referenced post couldn't be found."


class JoinRequestForm(RequestForm):
    request_type = Leadership.JOIN

    def clean_title(self):
        return "%s wants to join this chapter." % ( self._request.user.username )

    @classmethod
    def validate(self, user, data=None, bulletin=None):
        profile = user.get_profile()

        if not profile.can_apply():
            return "User is not eligible to apply."


class LeadRequestForm(RequestForm):
    request_type = Leadership.LEAD
    
    def clean_title(self):
        return "%s wants to become a leader." % ( self._request.user.username )

    @classmethod
    def validate(self, user, data=None, bulletin=None):
        profile = user.get_profile()

        if profile.is_leader:
            return "User is already a leader."


class LeadResignForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super(LeadResignForm, self).__init__(*args, **kwargs)
        self._request = request

    def clean(self):
        self.cleaned_data = super(LeadResignForm, self).clean()
        if not self._request.user.get_profile().is_leader:
            raise forms.ValidationError, "Only leaders can resign."

        return self.cleaned_data

    def save(self, commit=True):
        profile = self._request.user.get_profile()
        profile.resign_leadership(commit=False)

        if commit:
            profile.save()

        return profile


class PairRequestForm(RequestForm):
    request_type = Leadership.PAIR

    def clean(self):
        self.cleaned_data = super(PairRequestForm, self).clean()
        if self._request.user.get_profile().is_leader:
            raise forms.ValidationError, "Leaders cannot seek new mentors."

        return self.cleaned_data

    def clean_title(self):
        return "%s is seeking a new mentor." % ( self._request.user.username )


class HelpRequestForm(RequestForm):
    allow_multiple = True
    request_type = Leadership.HELP

    def clean_title(self):
        return "%s has a question." % ( self._request.user.username )

    def clean(self):
        self.cleaned_data = super(HelpRequestForm, self).clean()
        #if self._request.user.get_profile().is_leader:
        #    raise forms.ValidationError, "Leaders cannot seek help."

        return self.cleaned_data


#
# Process requests
#

class ResponseForm(forms.Form):
    # These rely on bulletin being bound in the request
    response = forms.IntegerField(min_value=Leadership.RESPONSE_MIN, max_value=Leadership.RESPONSE_MAX)

    def __init__(self, request, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)

        self._request = request
        self._valid = True

    def clean(self):
        if not self._errors:
            if not self._request.bulletin.can_respond():
                raise forms.ValidationError, "This request has already received a response."

            self._valid = getattr(self, 'request_form', None).validate(self._request.bulletin.owner, bulletin=self._request.bulletin) is None

        return self.cleaned_data

    def clean_response(self):
        response = self.cleaned_data.get('response', None)

        if response == Leadership.PENDING:
            raise forms.ValidationError, "Cannot mark a request as pending."

        return response

    def save(self):
        response = self.cleaned_data['response']

        if not self._valid:
            response = Leadership.CANCELED

        if response == Leadership.CANCELED:
            self._request.bulletin.cancel(self._request.user)
        elif response == Leadership.APPROVED:
            self._request.bulletin.approve(self._request.user)
        elif response == Leadership.DENIED:
            self._request.bulletin.deny(self._request.user)
        elif response == Leadership.ACTIVE:
            self._request.bulletin.activate(self._request.user)

        return response


class PromoteResponseForm(ResponseForm):
    request_form = PromoteRequestForm

    def save(self):
        response = super(PromoteResponseForm, self).save()

        if response == Leadership.APPROVED:
            self._request.bulletin.related.promote(self._request.user)

        return response


class JoinResponseForm(ResponseForm):
    request_form = JoinRequestForm

    def clean(self):
        super(JoinResponseForm, self).clean()

        return self.cleaned_data

    def save(self):
        profile = self._request.bulletin.owner.get_profile()
        response = super(JoinResponseForm, self).save()

        if response == Leadership.APPROVED:
            profile.approve_membership(self._request.user)

        elif response == Leadership.DENIED:
            profile.deny_membership()

        return response


class LeadResponseForm(ResponseForm):
    request_form = LeadRequestForm

    def save(self):
        profile = self._request.bulletin.owner.get_profile()
        response = super(LeadResponseForm, self).save()

        if response == Leadership.APPROVED:
            profile.become_leader()

        return response


class PairResponseForm(ResponseForm):
    request_form = PairRequestForm

    def clean(self):
        super(PairResponseForm, self).clean()

        if not self._errors:
            profile = self._request.user.get_profile()

            if not profile.available_to_lead():
                raise forms.ValidationError, "User has too many mentees."

        return self.cleaned_data

    def save(self):
        profile = self._request.bulletin.owner.get_profile()
        response = super(PairResponseForm, self).save()

        if response == Leadership.APPROVED:
            profile.assign_leader(self._request.user)

        return response


class HelpResponseForm(ResponseForm):
    request_form = HelpRequestForm
