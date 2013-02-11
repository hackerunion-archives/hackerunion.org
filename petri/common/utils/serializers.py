__author__ = "Brandon Diamond"

from django.utils.functional import Promise
from django.utils.translation import force_unicode

from django.db.models import Model
from django.db.models.query import QuerySet
from django.db.models.query import ValuesQuerySet

from django.utils import simplejson
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

class EnhancedJSONEncoder(DjangoJSONEncoder):
  "Extend default simplejson serializer to handle Django querysets and promises."
  def default(self, o):
    if isinstance(o, ValuesQuerySet):
      return list(o)
    elif isinstance(o, QuerySet):
      return list(o.values())
    elif isinstance(o, Promise):
      return force_unicode(o)
    
    return super(EnhancedJSONEncoder, self).default(o)


def serialize_json(obj, **options):
  "A helper performing enhanced json serialization (see above)."
  return simplejson.dumps(obj, cls=EnhancedJSONEncoder, **options)


def deserialize_json(json, **options):
  return simplejson.loads(json, **options)
