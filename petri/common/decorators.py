_author__ = "Brandon Diamond [brandon.t.diamond@gmail.com]"

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden

from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from django.utils import simplejson
from django.template.loader import render_to_string

from petri.common.utils.serializers import EnhancedJSONEncoder
from petri.common.utils import json

def anonymous_required(func):
  def wrap(request, *args, **kwargs):
    if request.user.is_anonymous():
      return func(request, *args, **kwargs)
    return HttpResponseRedirect('/')
  return wrap


def jsonify(func):
  def wrap(request, *args, **kwargs):
    response = None
    
    # Handle jsonp remote requests appropriately
    jsonp = (
      'callback' in request.REQUEST,
      request.REQUEST.get('callback', None)
    )

    try:
      response = func(request, *args, **kwargs)
      
      if not isinstance(response, dict):
        return response

    except Exception, e:
      if settings.DEBUG:
        import traceback
        response = json.error(traceback.format_exc())
      else:
        response = json.error("An error has occurred")

    if 'result' not in response:
      response['result'] = 'success'
		
    jsonstr = simplejson.dumps(response, cls=EnhancedJSONEncoder)

    if jsonp[0]:
      jsonstr = "%s(%s)" % (jsonp[1], jsonstr)

    return HttpResponse(jsonstr, mimetype='application/json')
  return wrap
