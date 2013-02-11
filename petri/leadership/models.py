from django.conf import settings

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save

from django.contrib.auth.models import User

from petri.bulletin.models import Bulletin
from petri.bulletin.models import connect_bulletin_signals

from petri.synergy.models import NotificationType, Notification


class LeadershipManager(models.Manager):
    def user_requests(self, owner):
        return self.filter(owner=owner)

    def leader_requests(self, leader=None):
        if leader is None:
            return self.filter(Q(response=Leadership.PENDING) | Q(response=Leadership.ACTIVE))

        # includes active requests
        return self.filter(processed_by=leader)

    def has_requested(self, owner, request, **kwargs):
        return self.filter(request=request, owner=owner, response=Leadership.PENDING, **kwargs).exists()


class Leadership(Bulletin):
    JOIN = 1
    LEAD = 2
    PAIR = 3
    HELP = 4
    PROMOTE = 5

    REQUEST_CHOICES = (
        (JOIN, "Join"),
        (LEAD, "Lead"),
        (PAIR, "Pair"),
        (HELP, "Help"),
        (PROMOTE, "Promote")
    )

    PENDING = 1
    APPROVED = 2
    DENIED = 3
    ACTIVE = 4
    CANCELED = 5

    RESPONSE_MAX = 5
    RESPONSE_MIN = 1

    RESPONSE_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (DENIED, "Denied"),
        (ACTIVE, "Active"),
        (CANCELED, "Canceled")
    )

    objects = LeadershipManager()

    request = models.IntegerField(choices=REQUEST_CHOICES)
    response = models.IntegerField(choices=RESPONSE_CHOICES, default=PENDING)
    processed_by = models.ForeignKey(User, related_name="processed_set", default=None, null=True)

    def get_request_name(self):
        return dict(Leadership.REQUEST_CHOICES)[self.request].lower()

    def is_invalid(self):
        return self.response == Leadership.CANCELED and self.processed_by is not None

    def can_respond(self):
        return self.response in (Leadership.PENDING, Leadership.ACTIVE)

    def can_cancel(self):
        return self.request in (Leadership.LEAD, Leadership.PAIR, Leadership.HELP)

    def cancel(self, user=None):
        self.response = Leadership.CANCELED
        self.processed_by = user
        self.save()

    def activate(self, user):
        self.response = Leadership.ACTIVE
        self.processed_by = user
        self.save()

    def approve(self, user):
        self.response = Leadership.APPROVED
        self.processed_by = user
        self.save()
        # Send out notifications
        if self.request == self.JOIN:
            notification_type = NotificationType.objects.get(name="membership_approved")
        else:
            notification_type = NotificationType.objects.get(name="leadership_approved")

        notification = Notification(notification_type=notification_type)
        notification.save()
        notification.users.add(self.owner)
        notification.add_dictionary({"chapter": self.chapter.slug, "processor": self.processed_by.get_profile().display_name, "request_title": self.title, "request_pk": self.pk})
        notification.save()
        notification.dispatch()

    def deny(self, user):
        self.response = Leadership.DENIED
        self.processed_by = user
        self.save()


def create_leadership(sender, instance, created, **kwargs):
    if created:
        notification_type = NotificationType.objects.get(name="new_leadership")
        notification = Notification(notification_type=notification_type)
        notification.save()
        from petri.account.models import UserProfile
        for leader_profile in UserProfile.objects.filter(chapter=instance.chapter, is_leader=True):
            if "?n=" + leader_profile.user.username.lower() not in instance.content:
                notification.users.add(leader_profile.user)
        notification.add_dictionary({"chapter": instance.chapter.slug, "bulletin": instance.pk, "title": instance.title, "content": instance.content})
        notification.save()
        notification.dispatch()


connect_bulletin_signals(Leadership)
post_save.connect(create_leadership, sender=Leadership)
