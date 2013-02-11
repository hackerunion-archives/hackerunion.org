from django.db import models
from django.contrib.auth.models import User

from petri.bulletin.models import Bulletin
from petri.bulletin.models import connect_bulletin_signals

from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.contrib.syndication.views import Feed
from petri.chapter.models import Chapter


class Talk(Bulletin):
    is_announcement = models.BooleanField(default=False)


class TalkFeed(Feed):

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
        return "/" + item.chapter.slug + "/" + str(item.pk)


connect_bulletin_signals(Talk)
