import re

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from petri.common.utils.models import InheritanceCastModel

from django.contrib.auth.models import User

class Tag(InheritanceCastModel):
    name = models.CharField(max_length=settings.TAG_MAX_LEN)

    def bulletins_by_type(self, cls, cast=True):
        result = self.bulletins.filter(actual_type=ContentType.objects.get_for_model(cls))

        if cast:
            result = [b.cast() for b in result]

        return result

    def save(self, *args, **kwargs):
        if self.id is None:
            self.name = re.sub(r'\s+', r' ', self.name).lower().strip()

        super(Tag, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.name)


class Skill(Tag):
    pass


class Affiliation(Tag):
    link = models.URLField()


class Initiative(Tag):
    project = models.OneToOneField('project.Project', unique=True)
