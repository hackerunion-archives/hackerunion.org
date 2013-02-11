from django import template

from django.utils.safestring import mark_safe

from petri.common.utils import json
from petri.common.utils.javascript import shrinkjs
from petri.common.utils.serializers import serialize_json

register = template.Library()

class PackedJSNode(template.Node):
  def __init__(self, nodelist):
    self.nodelist = nodelist

  def render(self, context):
    return shrinkjs(self.nodelist.render(context).strip())


@register.tag
def packjs(parser, token):
  "Compresses and obfuscates the body of the tag."
  nodelist = parser.parse(('endpackjs',))
  parser.delete_first_token()
  return PackedJSNode(nodelist)


@register.filter
def jsonify(raw, wrap=None):
  expr = raw

  if wrap:
    expr = json.success(raw) if wrap.lower()[0] == 's' else json.error(raw)
  
  return mark_safe(serialize_json(expr))
