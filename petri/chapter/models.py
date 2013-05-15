from django.db import models
from django.conf import settings

import re

from django.db.models.signals import post_save

from django.contrib.auth.models import User


class Chapter(models.Model):
    slug = models.SlugField()
    location = models.TextField()
    description = models.TextField(default="")
    markup = models.TextField(default="")
    founded = models.DateTimeField(auto_now_add=True)
    founder = models.ForeignKey(User, null=True, default=None, related_name="founded_set")
    custom_css = models.TextField(null=True, blank=True)
    base_color = models.TextField(null=True, blank=True)

    def get_announce_list(self):
        return settings.EMAIL_FORMAT % (settings.ANNOUNCE_LIST_FORMAT % self.slug)

    def get_official_list(self):
        return settings.EMAIL_FORMAT % (settings.OFFICIAL_LIST_FORMAT % self.slug)

    def get_discuss_list(self):
        return settings.EMAIL_FORMAT % (settings.DISCUSS_LIST_FORMAT % self.slug)

    def __unicode__(self):
        return unicode(self.location)


def chapter_post_save(sender, instance, created, **kwargs):
    if created:
        from petri.mail.utils import create_chapter_lists
        from petri.mail.utils import create_chapter_routes

        create_chapter_lists(instance)
        create_chapter_routes(instance)

    # update the scss file to update the chapter colors.
    if instance.base_color:
        with open(settings.CHAPTER_SCSS_DIR + instance.slug + ".scss", 'r+') as f:
            data = f.read()
            data = re.sub(r'\$primary-color:[^;]*', '$primary-color:' + instance.base_color, data)
            f.seek(0)
            f.write(data)
            f.truncate()


post_save.connect(chapter_post_save, sender=Chapter)
