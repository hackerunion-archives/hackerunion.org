import itertools 

from django.db import models
from django.db.models import Q

from petri.common.utils.helpers import ensure_tuple
from petri.common.utils.helpers import simplify_tuple

from django.contrib.contenttypes.models import ContentType

def filter_distinct(qset, **kwargs):
  # avoids dupes by reversing logic:
  # "return items excluding those that aren't related"
  return qset.exclude(~Q(**kwargs))


def owner_args(owner, owner_ip):
  return { 'owner_ip': owner_ip } if not owner or owner.is_anonymous() else { 'owner': owner }


def model_to_id(model):
  return getattr(model, 'id', model)


class InheritanceCastModel(models.Model):
  class Meta:
    abstract = True

  actual_type = models.ForeignKey(ContentType, null=True)

  def _get_actual_type(self):
    return ContentType.objects.get_for_model(type(self))

  def is_type(self, t):
    return t is self.actual_type.model_class()

  def save(self, *args, **kwargs):
    if self.id is None:
      self.actual_type = self._get_actual_type()

    super(InheritanceCastModel, self).save(*args, **kwargs)

  def cast(self):
    return self.actual_type.get_object_for_this_type(id=self.id)


class ValueBasedModelManager(models.Manager):
  def _value_fields(self):
    return ensure_tuple(getattr(self, 'VALUES', ('value',)))
  
  def _value_map(self, value, reverse=False):
    if reverse:
      return simplify_tuple(tuple(value[f] for f in self._value_fields()))
    
    return dict(itertools.izip(self._value_fields(), ensure_tuple(value)))


class ValueBasedModel(models.Model):
  class Meta:
    abstract = True

  objects = ValueBasedModelManager()

  def _value_fields(self):
    return self.__class__.objects._value_fields()

  def _value_map(self, value, reverse=False):
    return self.__class__.objects._value_map(value, reverse=reverse)

  def set_value(self, value, save=True):
    for attr, val in self._value_map(value).iteritems():
      setattr(self, attr, val)

    if save:
      self.save()

  def get_value(self, ids=False):
    # all models are converted to IDs (aggregation routines yield IDs, so scalar meta return IDs for consistency)
    return simplify_tuple(tuple((model_to_id if ids else (lambda _:_))(getattr(self, f, None)) for f in self._value_fields()))
