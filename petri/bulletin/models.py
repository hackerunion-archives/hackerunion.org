import datetime

from sanitizer.models import SanitizedTextField

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.html import strip_entities
from django.core.urlresolvers import reverse

from django.template.loader import render_to_string

from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User

from petri.common.utils.models import InheritanceCastModel

from petri.tag.models import Tag
from petri.chapter.models import Chapter
from petri.synergy.models import Notification, NotificationType

from petri.bulletin.utils import get_mentions, linkify_mentions

from petri.mail.utils import send_email
from django.shortcuts import get_object_or_404
from django.contrib.syndication.views import Feed


class Bulletin(InheritanceCastModel):
    title = models.CharField(max_length=settings.TITLE_MAX_LEN)
    content = SanitizedTextField(allowed_tags=['a', 'p', 'img', 'b', 'u', 'ul', 'li', 'tr', 'table', 'td', 'tbody', 'strike', 'ol', 'span', 'blockquote', 'hr', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'code', 'pre', 'i', 'br', 'iframe'],
                                 allowed_attributes=['href', 'src', 'width', 'height', 'style', 'id', 'frameborder'],
                                 allowed_styles=['width', 'height', 'color', 'background-color', 'text-align', 'margin', 'border', 'padding'], strip=True)
    owner = models.ForeignKey(User, related_name='owner')
    promoted_by = models.ForeignKey(User, related_name='promoted', null=True, default=None, blank=True)
    promoted_on = models.DateTimeField(null=True, default=None)
    followed_by = models.ManyToManyField(User, related_name="following")
    users_mentioned = models.ManyToManyField(User, related_name="mentioned")
    users_notified = models.ManyToManyField(User, related_name="notified")
    related = models.ForeignKey("self", null=True, default=None, blank=True)
    chapter = models.ForeignKey(Chapter)
    is_official = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="bulletins")
    created = models.DateTimeField(auto_now_add=True)
    thread_id = models.CharField(max_length=settings.THREAD_ID_LEN, null=True, blank=True, default=None)
    is_generated = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(User, related_name='moderated', null=True, default=None, blank=True)

    def get_list(self):
        if self.is_official:
            return self.chapter.get_official_list()

        return self.chapter.get_discuss_list()

    def can_broadcast(self):
        from petri.talk.models import Talk
        return not self.is_generated and type(self.cast()) is Talk
    
    def is_broadcast(self):
        return bool(self.thread_id)

    def can_notify(self):
        from petri.talk.models import Talk
        return not isinstance(self.cast(), Talk)

    def title_with_default(self, generate=True):
        default = "New message from %s" % self.owner.username

        if generate:
            snippet = self.content_plain()[:settings.TITLE_SNIPPET_LEN]

            if snippet.strip():
                default = ("%s..." % snippet).capitalize()

        return self.title or default

    def content_plain(self):
      return strip_entities(strip_tags(self.content))

    def follow(self, user):
        self.followed_by.add(user)

    def unfollow(self, user):
        self.followed_by.remove(user)

    def get_absolute_url(self):
        return reverse('bulletin.views.home', args=[str(self.id)])

    def unpromote(self):
        # leave promotion date to avoid double announcing
        self.promoted_by = None
        self.save()

    def promote(self, user):
        is_initial = self.promoted_on is None

        self.promoted_by = user
        self.promoted_on = datetime.datetime.now()
        self.save()

        return is_initial

    def is_promoted(self):
        return self.promoted_by is not None

    def render(self, profile, context={}):
        c = { 'bulletin': self, 'current_user_profile': profile }
        context.update(c)

        return render_to_string("%s/bulletin.jade" % self.cast().__class__.__name__.lower(), context)

    def render_text(self, context={}):
        c = { 'bulletin': self }
        context.update(c)

        return render_to_string("%s/bulletin_text.jade" % self.cast().__class__.__name__.lower(), context)

    def render_inline(self, profile, context={}):
        c = { 'bulletin': self, 'current_user_profile': profile }
        context.update(c)

        return render_to_string("%s/bulletin_inline.jade" % self.cast().__class__.__name__.lower(), context)

    def override_template(self):
        return False

    def get_chapter(self):
        return self.chapter

    def create_mention_notifications(self):
        add_users = []
        for user in self.users_mentioned.all():
            if user not in self.users_notified.all():
                add_users.append(user)

        if len(add_users) == 0:
            return

        notification_type = NotificationType.objects.get(name="new_mention")
        notification = Notification(notification_type=notification_type)
        notification.save()

        for user in add_users:
            notification.users.add(user)
            self.users_notified.add(user)

        notification.add_dictionary({"chapter": self.chapter.slug, "bulletin": self.pk})
        notification.save()
        notification.dispatch()

    def save(self, *args, **kwargs):
        matches = get_mentions(self.content)
        self.content = linkify_mentions(self)

        super(Bulletin, self).save(*args, **kwargs)
        for match in matches:
            try:
                user = User.objects.get(username__iexact=match.lower())
                self.users_mentioned.add(user)
            except User.DoesNotExist:
                continue

        self.create_mention_notifications()


class Comment(models.Model):
    owner = models.ForeignKey(User)
    bulletin = models.ForeignKey(Bulletin)
    content = SanitizedTextField(allowed_tags=['a', 'p', 'img', 'b', 'u', 'ul', 'li', 'tr', 'table', 'td', 'tbody', 'strike', 'ol', 'span', 'blockquote', 'hr', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'code', 'pre', 'i', 'br', 'iframe'],
                                 allowed_attributes=['href', 'src', 'width', 'height', 'style', 'id', 'frameborder'],
                                 allowed_styles=['width', 'height', 'color', 'background-color', 'text-align', 'margin', 'border', 'padding'], strip=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users_mentioned = models.ManyToManyField(User, related_name="comment_mentioned")
    users_notified = models.ManyToManyField(User, related_name="comment_notified")
    thread_id = models.CharField(max_length=settings.THREAD_ID_LEN, null=True, blank=True, default=None)
    is_generated = models.BooleanField(default=False)
    
    def can_broadcast(self):
        return not self.is_generated and self.bulletin.is_broadcast()

    def can_notify(self):
        return self.bulletin.can_notify()

    def get_chapter(self):
        return self.bulletin.chapter

    def create_mention_notifications(self):
        add_users = []
        for user in self.users_mentioned.all():
            if user not in self.users_notified.all():
                add_users.append(user)

        if len(add_users) == 0:
            return

        notification_type = NotificationType.objects.get(name="new_mention")
        notification = Notification(notification_type=notification_type)
        notification.save()

        for user in add_users:
            notification.users.add(user)
            self.users_notified.add(user)

        notification.add_dictionary({"chapter": self.bulletin.chapter.slug, "bulletin": self.bulletin.pk, "comment": self.pk})
        notification.save()
        notification.dispatch()

    def save(self, *args, **kwargs):
        matches = get_mentions(self.content)
        self.content = linkify_mentions(self)

        super(Comment, self).save(*args, **kwargs)
        for match in matches:
            try:
                user = User.objects.get(username__iexact=match.lower())
                self.users_mentioned.add(user)
            except User.DoesNotExist:
                continue

        self.create_mention_notifications()

    def __unicode__(self):
        return unicode(self.content)


class BulletinFeed(Feed):

    def get_object(self, request, chapter_slug):
        return get_object_or_404(Chapter, slug=chapter_slug)

    def title(self, obj):
        return "Hacker Union %s" % obj.location

    def link(self, obj):
        return "/%s/" % obj.slug

    def description(self, obj):
        return "Recent Updates in Hacker Union %s" % obj.location

    def items(self, obj):
        return Bulletin.objects.filter(chapter=obj, is_official=False).order_by('-created')[:10]

    def item_title(self, item):
        return item.content[:100] + "..." if len(item.content) > 100 else item.content

    def item_description(self, item):
        return item.content

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return "/" + item.chapter.slug + "/posts/" + str(item.pk)


# TODO: optimize this mofo
def _create_comment(sender, instance, created, **kwargs):
    if created:
        if instance.can_notify():
            notification_type = NotificationType.objects.get(name="new_comment")
            notification = Notification(notification_type=notification_type)
            notification.save()
            if instance.bulletin.owner.pk != instance.owner.pk:
                notification.users.add(instance.bulletin.owner)
            for comment in Comment.objects.filter(bulletin=instance.bulletin):
                if comment.bulletin.owner.pk != comment.owner.pk and comment.owner.pk != instance.owner.pk:
                    notification.users.add(comment.owner)
            for follower in instance.bulletin.followed_by.all():
                if follower.pk != comment.owner.pk and follower.pk != instance.owner.pk:
                    notification.users.add(follower)
            notification.add_dictionary({"chapter": instance.bulletin.chapter.slug, "bulletin": instance.bulletin.pk, "comment": instance.pk})
            notification.save()
            notification.dispatch()


def _broadcast_bulletin(sender, instance, created, **kwargs):
    if created and instance.can_broadcast():
        # try to send email (ignore failures - this is a best effort process)
        instance.thread_id = send_email(to=instance.get_list(),
                                        subject=instance.title_with_default(),
                                        sender=instance.owner.email,
                                        body=instance.content,
                                        internal=True)

        # avoid signal recursion
        post_save.disconnect(_broadcast_bulletin, sender=Bulletin)
        instance.save()
        post_save.connect(_broadcast_bulletin, sender=Bulletin)


def _broadcast_comment(sender, instance, created, **kwargs):
    if created and instance.can_broadcast():
        # try to send email (ignore failures - this is a best effort process)
        instance.thread_id = send_email(to=instance.bulletin.get_list(),
                                        subject="Re: %s" % instance.bulletin.title_with_default(),
                                        sender=instance.owner.email,
                                        body=instance.content,
                                        reply=instance.bulletin.thread_id,
                                        internal=True)

        # avoid signal recursion
        post_save.disconnect(_broadcast_comment, sender=Comment)
        instance.save()
        post_save.connect(_broadcast_comment, sender=Comment)


# TODO: remove this once virtual signal handling exists
def connect_bulletin_signals(sender=Bulletin):
    # virtual signals don't work (superclass signals not triggered by subclass)
    # manually attach signals to subclasses using this helper until fix created
    # https://code.djangoproject.com/ticket/9318
    post_save.connect(_broadcast_bulletin, sender=sender)


connect_bulletin_signals()

post_save.connect(_broadcast_comment, sender=Comment)
post_save.connect(_create_comment, sender=Comment)
