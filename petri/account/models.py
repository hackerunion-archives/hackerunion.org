import os
from binascii import hexlify

from django.conf import settings

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.template.loader import render_to_string

from petri.chapter.models import Chapter
from petri.bulletin.models import Bulletin
from petri.tag.models import Skill, Affiliation, Initiative

from petri.leadership.utils import create_pair_request

from petri.mail.utils import proxy_email
from petri.mail.utils import subscribe_list
from petri.mail.utils import unsubscribe_list

import petri.synergy


def _create_invite_code():
    return hexlify(os.urandom(settings.INVITATION_CODE_LENGTH / 2))


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    email_notifications = models.BooleanField(default=True)

    NO_DIGEST = 1
    DAILY_DIGEST = 2
    WEEKLY_DIGEST = 3
    MONTHLY_DIGEST = 4
    DIGEST_CHOICES = (
        (NO_DIGEST, 'None'),
        (DAILY_DIGEST, 'Daily'),
        (WEEKLY_DIGEST, 'Weekly'),
        (MONTHLY_DIGEST, 'Inactive')
    )

    email_digest = models.IntegerField(choices=DIGEST_CHOICES, default=WEEKLY_DIGEST)

    allow_discuss = models.BooleanField(default=True)
    allow_official = models.BooleanField(default=True)
    allow_announce = models.BooleanField(default=True)

    PENDING = 1
    APPROVED = 2
    DENIED = 3
    INACTIVE = 4
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied'),
        (INACTIVE, 'Inactive')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    is_leader = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

    chapter = models.ForeignKey(Chapter, null=False, default=1)
    starred = models.ManyToManyField(Bulletin, blank=True)
    invitation_count = models.IntegerField(default=5)
    leader = models.ForeignKey(User, null=True, blank=True, related_name="mentees")

    skills = models.ManyToManyField(Skill, blank=True)
    affiliations = models.ManyToManyField(Affiliation, blank=True)
    initiatives = models.ManyToManyField(Initiative, blank=True)

    gravatar_email = models.EmailField(null=True, blank=True)

    facebook_url = models.URLField(default="", null=True, blank=True)
    twitter_url = models.URLField(default="", null=True, blank=True)
    linkedin_url = models.URLField(default="", null=True, blank=True)
    github_url = models.URLField(default="", null=True, blank=True)
    dribble_url = models.URLField(default="", null=True, blank=True)

    display_name = models.CharField(max_length=30)

    show_guide = models.BooleanField(default=True)

    def has_mentee(self, user):
        return self.is_leader and user.get_profile().leader == self.user

    def can_moderate(self):
        return self.is_leader and self.is_moderator

    def sent_invites(self, only_pending=False):
        qs = self.user.invitation_set.all()

        if only_pending:
            return qs.filter(is_active=True)

        return qs

    def can_invite(self):
        return self.available_to_lead()

    def available_to_lead(self):
        return self.is_leader and self.get_mentees().count() < settings.MAX_MENTEES

    def get_mentees(self):
        return self.user.mentees.all()

    def become_moderator(self):
        if self.can_moderate():
            return

        if not self.is_leader:
            self.become_leader()

        self.is_moderator = True
        self.save()

    def resign_moderation(self):
        if not self.can_moderate():
            return

        self.is_moderator = False
        self.save()

    def become_leader(self):
        if self.is_leader:
            return

        self.is_leader = True
        self.leader = None
        self.save()

        if self.allow_official:
            subscribe_list(self.chapter.get_official_list(), self.get_email(proxy=False))

    def assign_leader(self, user, commit=True):
        self.leader = user

        if commit:
            self.save()

    def abandon(self, commit=True):
        self.assign_leader(None, commit=commit)

    def resign_leadership(self, commit=True):
        self.resign_moderation()

        if not self.is_leader:
            return

        self.is_leader = False

        for mentee in self.get_mentees():
            mentee.leader = None
            mentee.save()

            create_pair_request(mentee.user, self.chapter, "My mentor (%s) stepped down as a leader." % self.display_name)

        if commit:
            self.save()

        unsubscribe_list(self.chapter.get_official_list(), self.get_email(proxy=False))

    def associate(self, chapter, commit=True):
        # make user a pending member of the chapter
        self.chapter = chapter

        if commit:
            self.save()

    def activate(self, chapter, leader, commit=True):
        # make user an active member of the chapter
        self.status = UserProfile.APPROVED
        self.chapter = chapter
        if leader.get_profile().available_to_lead():
            self.assign_leader(leader, commit=commit)
        else:
            self.assign_leader(None, commit=commit)

        proxy_email(self.get_email(proxy=False), self.user.username, relative=True, unproxy=True)

        if self.allow_announce:
            subscribe_list(self.chapter.get_announce_list(), self.get_email(proxy=False))

        if self.allow_discuss:
            subscribe_list(self.chapter.get_discuss_list(), self.get_email(proxy=False))

    def deactivate(self):
        unsubscribe_list(self.chapter.get_announce_list(), self.get_email(proxy=False))
        unsubscribe_list(self.chapter.get_discuss_list(), self.get_email(proxy=False))

        # make user an inactive, detached user
        self.resign_leadership(commit=False)
        self.leader = None
        self.chapter = None
        self.status = UserProfile.INACTIVE
        self.save()

    def is_inactive(self):
        return self.status == UserProfile.INACTIVE

    def manage_official(self, allow):
        if not self.is_leader:
            return

        self.allow_official = allow
        self.save()

        if allow:
            subscribe_list(self.chapter.get_official_list(), self.get_email(proxy=False))
        else:
            unsubscribe_list(self.chapter.get_official_list(), self.get_email(proxy=False))

    def manage_discuss(self, allow):
        self.allow_discuss = allow
        self.save()

        if allow:
            subscribe_list(self.chapter.get_discuss_list(), self.get_email(proxy=False))
        else:
            unsubscribe_list(self.chapter.get_discuss_list(), self.get_email(proxy=False))

    def manage_announce(self, allow):
        self.allow_announce = allow
        self.save()

        if allow:
            subscribe_list(self.chapter.get_announce_list(), self.get_email(proxy=False))
        else:
            unsubscribe_list(self.chapter.get_announce_list(), self.get_email(proxy=False))

    def approve_membership(self, leader):
        self.activate(self.chapter, leader)

    def deny_membership(self):
        self.status = UserProfile.DENIED
        self.save()

    def get_email(self, proxy=True):
        return (settings.EMAIL_FORMAT % self.user.username) if proxy else self.user.email

    def can_apply(self):
        return self.has_chapter() and self.status not in (UserProfile.APPROVED, UserProfile.DENIED)

    def is_member(self, chapter=None):
        return self.has_chapter() and self.status == UserProfile.APPROVED and (chapter is None or self.chapter == chapter)

    def is_insider(self):
        return self.is_member(chapter=None)

    def is_outsider(self):
        return not self.is_insider()

    def is_pending(self):
        return self.status == UserProfile.PENDING

    def has_chapter(self):
        return self.chapter != None

    def get_gravatar_email(self):
        return self.gravatar_email if self.gravatar_email else self.get_email(proxy=False)

    def has_no_social(self):
        return not (self.facebook_url or
                    self.twitter_url or
                    self.linkedin_url or
                    self.github_url or
                    self.dribble_url)

    def has_no_skills(self):
        return not self.skills.all() and not self.affiliations.all() and not self.initiatives.all()

    def __unicode__(self):
        return unicode(self.user)


class Invitation(models.Model):
    code = models.CharField(default=_create_invite_code, max_length=settings.INVITATION_CODE_LENGTH)
    sponsor = models.ForeignKey(User)
    chapter = models.ForeignKey('chapter.Chapter')
    is_active = models.BooleanField(default=True)
    target = models.EmailField(null=True, blank=True)

    def activate(self, user):
        profile = user.get_profile()
        profile.activate(self.chapter, self.sponsor)

        self.is_active = False
        self.save()


def create_invitation(sender, instance, created, **kwargs):
    if created and instance.target:
        notification_type = petri.synergy.models.NotificationType.objects.get(name="invite_site")
        invitation = petri.synergy.models.Invitation(notification_type=notification_type)
        invitation.save()
        invitation.to_email = instance.target
        invitation.add_dictionary({"chapter": instance.sponsor.get_profile().chapter.slug, "sponsor": instance.sponsor.pk, "invite_code": instance.code, "username": instance.sponsor.username, "display_name": instance.sponsor.get_profile().display_name })
        invitation.dispatch()
        invitation.save()


def create_user_profile(sender, instance, created, **kwargs):
    if created and not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)


post_save.connect(create_invitation, sender=Invitation)
post_save.connect(create_user_profile, sender=User)
