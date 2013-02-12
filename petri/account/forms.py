import re

from django.conf import settings

from django import forms

from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.db.models import Q

import petri.synergy

from petri.common.utils.forms import MultipleEmailsField
from petri.common.utils.forms import SmartNullBooleanField

from petri.account.models import Invitation, UserProfile
from petri.chapter.models import Chapter
from petri.tag.models import Tag, Skill, Affiliation

from petri.leadership.utils import bootstrap_join_request


class AbandonForm(forms.Form):
    user = forms.ModelChoiceField(User)
    
    def __init__(self, request, *args, **kwargs):
        super(AbandonForm, self).__init__(*args, **kwargs)
        
        self._request = request
        self.fields['user'].queryset = User.objects.filter(userprofile__leader=request.user, userprofile__leader__userprofile__is_leader=True)

    def save(self):
        self.cleaned_data['user'].get_profile().abandon()


class BanForm(forms.Form):
    username = forms.CharField(required=True)
    
    def __init__(self, request, *args, **kwargs):
        super(BanForm, self).__init__(*args, **kwargs)

        self._user = None
        self._request = request

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username:
            try:
                query = Q(username__iexact=username)
                
                # non-moderators can only ban own mentees
                if not self._request.user.get_profile().can_moderate():
                  query &= Q(userprofile__leader=self._request.user)

                self._user = User.objects.get(username__iexact=username)

            except User.DoesNotExist:
                raise forms.ValidationError, "Invalid user."

        return username

    def clean(self):
        if not self._request.user.get_profile().is_leader:
            raise forms.ValidationError, "Only guides can ban users."

        return self.cleaned_data

    def save(self):
        self._user.get_profile().deactivate()


class TransferForm(forms.Form):
    mentee = forms.CharField(required=True)
    leader = forms.CharField(required=True)

    def __init__(self, request, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)

        self._mentee = None
        self._leader = None
        self._request = request

    def clean_mentee(self):
        mentee = self.cleaned_data.get('mentee')

        if mentee:
            try:
                self._mentee = User.objects.get(username__iexact=mentee, userprofile__is_leader=False)
            except User.DoesNotExist:
                raise forms.ValidationError, "Invalid mentee."

        return mentee

    def clean_leader(self):
        leader = self.cleaned_data.get('leader')

        if leader:
            try:
                self._leader = User.objects.get(username__iexact=leader, userprofile__is_leader=True)
            except User.DoesNotExist:
                raise forms.ValidationError, "Invalid guide."
            
            if not self._leader.get_profile().available_to_lead():
                raise forms.ValidationError, "Unavailable to guide."

        return leader

    def clean(self):
        if not self._request.user.get_profile().can_moderate():
            raise forms.ValidationError, "Only moderators can use this feature."
        
        return self.cleaned_data

    def save(self):
        self._mentee.get_profile().assign_leader(self._leader)


class ModeratorForm(forms.Form):
    username = forms.CharField(required=True)
    grant = forms.BooleanField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(ModeratorForm, self).__init__(*args, **kwargs)

        self._user = None
        self._request = request

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username:
            try:
                self._user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                raise forms.ValidationError, "Invalid user."

        return username

    def clean(self):
        if not self._request.user.get_profile().can_moderate():
            raise forms.ValidationError, "Only moderators can use this feature."

        return self.cleaned_data

    def save(self):
        if self.cleaned_data.get('grant'):
            self._user.get_profile().become_moderator()
        else:
            self._user.get_profile().resign_moderation()


class GuideForm(forms.Form):
    username = forms.CharField(required=True)
    grant = forms.BooleanField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(GuideForm, self).__init__(*args, **kwargs)

        self._user = None
        self._request = request

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username:
            try:
                self._user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                raise forms.ValidationError, "Invalid user."

        return username

    def clean(self):
        profile = self._request.user.get_profile()

        if not profile.can_moderate():
            if not (profile.is_leader and self._user.get_profile().leader == self._request.user):
                raise forms.ValidationError, "This is a restricted feature."

        return self.cleaned_data

    def save(self):
        if self.cleaned_data.get('grant'):
            self._user.get_profile().become_leader()
        else:
            self._user.get_profile().resign_leadership()


class MarkupForm(forms.Form):
    markup = forms.CharField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(MarkupForm, self).__init__(*args, **kwargs)
        self._request = request

    def clean(self):
        if not self._request.user.get_profile().can_moderate():
            raise forms.ValidationError, "Only moderators can use this feature."

        return self.cleaned_data

    def save(self):
        chapter = self._request.user.get_profile().chapter

        if chapter:
            chapter.markup = self.cleaned_data.get('markup')
            chapter.save()


class NoticeForm(forms.Form):
    official = SmartNullBooleanField(required=False)
    discuss = SmartNullBooleanField(required=False)
    announce = SmartNullBooleanField(required=False)
    digest = forms.ChoiceField(choices=UserProfile.DIGEST_CHOICES, required=False)
    
    def __init__(self, request, *args, **kwargs):
        super(NoticeForm, self).__init__(*args, **kwargs)
        self._request = request

    def save(self):
        profile = self._request.user.get_profile()
        official = self.cleaned_data.get('official') if profile.is_leader else None
        discuss = self.cleaned_data.get('discuss')
        announce = self.cleaned_data.get('announce')
        digest = self.cleaned_data.get('digest')
        
        if official is not None:
            profile.manage_official(official)

        if discuss is not None:
            profile.manage_discuss(discuss)

        if announce is not None:
            profile.manage_announce(announce)

        if digest:
            profile.email_digest = digest
            profile.save()


class AccountApplicationForm(UserCreationForm):
    application = forms.CharField(max_length=settings.APPLICATION_MAX_LEN, widget=forms.widgets.Textarea(), min_length=settings.APPLICATION_MIN_LEN, required=False)
    invitation_code = forms.CharField(max_length=settings.INVITATION_CODE_LENGTH, required=False, label="Invite Code?")
    email = forms.EmailField(label="Email")
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.all(), empty_label=None)

    display_name = forms.RegexField(label=_("Display Name"), max_length=30,
        regex=r'^[ \w-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits, spaces, hyphens and "
                      "_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers, spaces and "
                         "_ characters.")})

    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "_ characters.")})

    def __init__(self, request, *args, **kwargs):
        super(AccountApplicationForm, self).__init__(*args, **kwargs)
        self._request = request

    def save(self, commit=True):
        user = super(AccountApplicationForm, self).save(commit=commit)
        user.email = self.cleaned_data.get("email")
        profile = user.get_profile()
        profile.display_name = self.cleaned_data.get("display_name")
        invited = False
        application = self.cleaned_data.get("application")

        chapter = self.cleaned_data.get("chapter")
        invitation_code = self.cleaned_data.get("invitation_code")

        profile.associate(chapter, commit=False)

        if invitation_code:
            try:
                invite = Invitation.objects.get(code=invitation_code)
            except Invitation.DoesNotExist:
                invite = None
            if invite and invite.chapter == chapter and invite.is_active:
                invite.activate(user)
                invited = True

        profile.save()
        user.save()

        if not invited:
            bootstrap_join_request(user, chapter, application, request=self._request)

        return user

    def clean_display_name(self):
        data = self.cleaned_data['display_name']
        if data.strip() == "":
            raise forms.ValidationError("Name is Invalid")
        if not data.strip()[0].isalpha():
            raise forms.ValidationError("Must start with a letter")
        return data.strip()

    def clean_username(self):
        data = self.cleaned_data['username']
        if data.strip() == "":
            raise forms.ValidationError("Name is Invalid")
        if not data.strip()[0].isalpha():
            raise forms.ValidationError("Must start with a letter")
        return data.strip().lower()

    def clean(self):
        cleaned_data = super(AccountApplicationForm, self).clean()
        application = cleaned_data.get("application")
        invitation_code = cleaned_data.get("invitation_code")
        chapter = cleaned_data.get("chapter")

        if invitation_code:
            try:
                invite = Invitation.objects.get(code=invitation_code)
            except Invitation.DoesNotExist:
                invite = None
            if invite and invite.chapter.pk == chapter.pk and invite.is_active:
                return cleaned_data
            else:
                raise forms.ValidationError("Invalid Invitation Code")
        elif application:
            return cleaned_data

        raise forms.ValidationError("Must include an invite code or an essay")

        # Always return the full collection of cleaned data.
        return cleaned_data


class FrontpageApplyForm(forms.Form):

    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[ \w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})

    email = forms.EmailField(label="Email")
    password = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)

    def clean_username(self):
        data = self.cleaned_data['username']
        if data.strip() == "":
            raise forms.ValidationError("Name is Invalid")

        return data


class AccountSocialForm(forms.ModelForm):

    def save(self, user_profile):
        if self.cleaned_data['facebook_url'].strip() != "":
            user_profile.facebook_url = self.cleaned_data['facebook_url']
        if self.cleaned_data['twitter_url'].strip() != "":
            user_profile.twitter_url = self.cleaned_data['twitter_url']
        if self.cleaned_data['linkedin_url'].strip() != "":
            user_profile.linkedin_url = self.cleaned_data['linkedin_url']
        if self.cleaned_data['github_url'].strip() != "":
            user_profile.github_url = self.cleaned_data['github_url']
        if self.cleaned_data['dribble_url'].strip() != "":
            user_profile.dribble_url = self.cleaned_data['dribble_url']
        if self.cleaned_data['gravatar_email'].strip() != "":
            user_profile.gravatar_email = self.cleaned_data['gravatar_email']
        user_profile.save()

    class Meta:
        model = UserProfile
        fields = ("facebook_url", "twitter_url", "linkedin_url", "github_url", "dribble_url", "gravatar_email")


class AccountEmailForm(forms.ModelForm):

    def save(self, user_profile):
        user_profile.email_notifications = self.cleaned_data['email_notifications']
        user_profile.email_digest = self.cleaned_data['email_digest']
        user_profile.save()

    class Meta:
        model = UserProfile
        fields = ("email_notifications", "email_digest")


class AccountSkillForm(forms.Form):
    skills = forms.CharField(required=False)
    affiliations = forms.CharField(required=False)

    def clean_skills(self):
        return [s.strip().lower() for s in self.cleaned_data.get('skills', '').split(',') if s.strip()]
    
    def clean_affiliations(self):
        return [s.strip().lower() for s in self.cleaned_data.get('affiliations', '').split(',') if s.strip()]

    def save(self, user_profile):
        user_profile.skills.clear()
        user_profile.affiliations.clear()
        
        skills = self.cleaned_data.get('skills')
        affiliations = self.cleaned_data.get('affiliations')
        
        if skills:
            for name in skills:
                skill, created = Skill.objects.get_or_create(name=name)
                user_profile.skills.add(skill)
        
        if affiliations:
            for name in affiliations:
                affiliation, created = Affiliation.objects.get_or_create(name=name)
                user_profile.affiliations.add(affiliation)

        user_profile.save()


class InviteForm(forms.Form):
    target = MultipleEmailsField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)

        self._request = request
        self._valid = True

    def clean(self):
        if not self._errors:
            profile = self._request.user.get_profile()

            if not profile.can_invite():
                # we tolerate and use the opportunity to send a "soft" invite
                self._valid = False

        return self.cleaned_data

    def save(self):
        profile = self._request.user.get_profile()
        targets = self.cleaned_data.get("target")

        if not targets:
            return None

        if self._valid:
            return Invitation.objects.create(sponsor=self._request.user, chapter=profile.chapter, target=targets[0]).code

        # send referral email
        notification_type = petri.synergy.models.NotificationType.objects.get(name="invite_site")
        username = self._request.user.username
        display_name = self._request.user.get_profile().display_name

        for target in targets:
          referral = petri.synergy.models.Invitation(notification_type=notification_type)
          referral.save()
          referral.to_email = target
          referral.add_dictionary({"chapter": profile.chapter.slug, "username": username, "display_name": display_name })
          referral.dispatch()
          referral.save()


