import re

from django.conf import settings
from django.utils import simplejson as json

from twilio import util
from twilio.rest import TwilioRestClient

from petri.common.utils.debug import debug

class TwilioException(Exception):
  pass


def _get_client():
  return TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_AUTH)


def _get_utils():
  return util.RequestValidator(settings.TWILIO_AUTH)



def outgoing_call(number, callback):
  try:
    callObj = _get_client().calls.create(from_=settings.TWILIO_CALLER, to=number, url=callback)
  except Exception, e:
    debug(str(e.__dict__), system="twilio-call")
    raise TwilioException(e.message)

  return callObj.status not in ['failed', 'busy', 'no-answer']


def outgoing_sms(number, body):
  try:
    smsObj = _get_client().sms.messages.create(from_=settings.TWILIO_TEXTER, to=number, body=body)
  except Exception, e:
    debug(str(e.__dict__), system="twilio-sms")
    raise TwilioException(e.message)
  
  return smsObj.status != 'failed'


def validate_request(request):
  return _get_utils().validate("http://%s%s" % (request.get_host(), request.get_full_path()),
                               request.POST,
                               request.META.get('HTTP_X_TWILIO_SIGNATURE', ''))
