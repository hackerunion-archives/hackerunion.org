import json
import email.utils

from django.conf import settings

from django.db.models import Q

from django import forms
from django.contrib.auth.models import User

from petri.chapter.models import Chapter
from petri.bulletin.models import Comment
from petri.bulletin.models import Bulletin

from petri.talk.models import Talk

class MailForm(forms.Form):
    NEW_MAIL = 1

    insiders_only = False
    members_only = False
    leaders_only = False
    ignore_internal = False
    require_id = False

    recipient = forms.CharField(required=True)
    sender = forms.CharField(required=True)
    message_from = forms.CharField(required=True)
    subject = forms.CharField()
    body_plain = forms.CharField()
    body_html = forms.CharField()
    stripped_html = forms.CharField()
    stripped_text = forms.CharField()
    stripped_signature = forms.CharField(required=False)
    content_id_map = forms.CharField(required=False)
    message_id = forms.CharField()
    message_headers = forms.CharField()
    in_reply_to = forms.CharField(required=False)
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        data = kwargs.get('data', {})
        scrub = {}
        
        self._user = None
        self._attachments = []

        for k, v in data.iteritems():
            if k.startswith("attachment-"):
                # TODO decode these as multipart/form-data
                self._attachments.append(v)
                continue

            # can't use from (it's a reserved word)
            if k == "from":
                k = "message_from"

            scrub[k.replace("-", "_").lower()] = v

        kwargs['data'] = scrub
        super(MailForm, self).__init__(*args, **kwargs)

    def clean_recipient(self):
        recipient = self.cleaned_data.get('recipient', '')

        if recipient:
            name, recipient = email.utils.parseaddr(recipient)

        return recipient

    def clean_sender(self):
        sender = self.cleaned_data.get('sender', '')

        if sender:
            name, sender = email.utils.parseaddr(sender)

        return sender

    def clean_message_from(self):
        message_from = self.cleaned_data.get('message_from', '')

        if message_from:
            name, message_from = email.utils.parseaddr(message_from)

        return message_from

    def clean_content_id_map(self):
        content_id_map = self.cleaned_data.get('content_id_map')

        if content_id_map:
            try:
                content_id_map = json.loads(content_id_map)
            except:
                raise forms.ValidationError, "Couldn't deserialize the content ID map."

        return content_id_map

    def clean_message_headers(self):
        message_headers = self.cleaned_data.get('message_headers')

        if message_headers:
            try:
                message_headers = json.loads(message_headers)
            except:
                raise forms.ValidationError, "Couldn't deserialize the message headers."

        return message_headers
    
    def is_reply(self):
        return bool(self.cleaned_data.get('in_reply_to', None))

    def get_reply_bulletin(self):
        # TODO make this more robust
        if self.is_reply():
            thread_id = self.cleaned_data.get('in_reply_to')
            bulletins = Bulletin.objects.filter(Q(thread_id=thread_id) | Q(comment__thread_id=thread_id))
            
            if bulletins.exists():
                return bulletins[0]

        return None

    def get_thread_id(self):
        # we call message IDs "thread IDs" internally (used by bulletins for threading)
        return self.cleaned_data.get('message_id') or ''

    def get_user(self):
        return self._user

    def get_best_subject(self, generate=True):
        return self.cleaned_data.get('subject', 'New post' if generate else None)

    def get_best_content(self, generate=True):
        return self.cleaned_data.get('stripped_html', self.cleaned_data.get('body_html', self.cleaned_data.get('stripped_text', self.cleaned_data.get('body_plain', '(This is an empty message)' if generate else None))))

    def get_header(self, header, multi=True):
        values = [v for k, v in self.cleaned_data.get('message_headers', []) if k == header]

        if multi:
            return values

        return values.pop(0) if values else None

    def get_chapter(self):
        return self.cleaned_data['chapter']

    def clean(self):
        if not self._errors:
            expr = Q()
            from_val = self.cleaned_data.get('message_from')
            chapter = self.cleaned_data.get('chapter')
            need_user = False
            
            # ignore emails that are internal
            if self.ignore_internal and self.get_header(settings.INTERNAL_EMAIL_HEADER):
                raise forms.ValidationError, "Cannot process internal emails"
            
            # ignore emails that are missing a message id [and is not a reply]
            if self.require_id and (self.require_id != MailForm.NEW_MAIL or not self.is_reply()) and not self.get_thread_id():
                raise forms.ValidationError, "Message is missing an ID"

            if self.leaders_only:
                expr &= Q(userprofile__is_leader=True)
                self.members_only = True
                need_user = True
    
            if self.members_only:
                if not chapter:
                    raise forms.ValidationError, "A valid chapter is required"

                expr &= Q(userprofile__chapter=chapter)
                self.insiders_only = True
                need_user = True
    
            if self.insiders_only:
                expr &= Q(email__iexact=from_val)
                need_user = True
            
            users = User.objects.filter(expr)
            
            # validate from if restrictions are requested
            if not users.exists():
                if need_user:
                    raise forms.ValidationError, "Unauthorized posting."
            
            self._user = users[0]

            # disallow emails without any content
            if not self.get_best_content(generate=False):
                raise forms.ValidationError, "Email cannot be blank"
            
        # TODO replace CID in html version with inline base64 encoded images
        return self.cleaned_data


class BroadcastMailForm(MailForm):
    require_id = MailForm.NEW_MAIL
    members_only = True
    ignore_internal = True

    def save(self, is_official=False):
        reply_to = self.get_reply_bulletin()

        if reply_to:
            return Comment.objects.create(owner=self.get_user(),
                                          bulletin=reply_to,
                                          content=self.get_best_content(),
                                          thread_id=self.get_thread_id(),
                                          is_generated=True)
       
        return Talk.objects.create(title=self.get_best_subject(),
                                   content=self.get_best_content(),
                                   owner=self.get_user(),
                                   chapter=self.get_chapter(),
                                   is_official=is_official,
                                   thread_id=self.get_thread_id(),
                                   is_generated=True)


class BroadcastOfficialForm(BroadcastMailForm):
    leaders_only = True

    def save(self, *args, **kwargs):
        kwargs['is_official'] = True
        return super(BroadcastOfficialForm, self).save(*args, **kwargs)
