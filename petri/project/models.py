from django.conf import settings

from django.db import models
from django.db import IntegrityError

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from petri.talk.models import Talk
from petri.event.models import Event

from petri.bulletin.models import Bulletin
from petri.bulletin.models import connect_bulletin_signals

from petri.tag.models import Initiative


class Project(Bulletin):
    picture = models.URLField(default=None, null=True, blank=True)

    @classmethod
    def attach_tag(cls, sender, instance, created, **kwargs):
        if created:
          name = instance.title.lower()[:settings.TAG_MAX_LEN]
  
          # this code assumes primary keys will never be re-used (even after delete)
          if Initiative.objects.filter(name=name).exists():
              uniq = "-%d" % (Initiative.objects.order_by('-id')[0].pk)
              name = name[:settings.TAG_MAX_LEN-len(uniq)] + uniq
  
          ini, tag_created = Initiative.objects.get_or_create(project=instance, defaults={ "name": name })
          
          if not tag_created:
              ini.name = name
              ini.save()

    def override_template(self):
        return "project/project.jade"

    def related_talk(self):
        return self.initiative.bulletins_by_type(Talk)

    def related_events(self):
        return self.initiative.bulletins_by_type(Event)

    def follow(self, user):
        super(Project, self).follow(user)

        profile = user.get_profile()
        profile.initiatives.add(self.initiative)

    def unfollow(self, user):
        super(Project, self).unfollow(user)

        profile = user.get_profile()
        profile.initiatives.remove(self.initiative)


connect_bulletin_signals(Project)
post_save.connect(Project.attach_tag, sender=Project)
