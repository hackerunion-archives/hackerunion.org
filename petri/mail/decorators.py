from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from petri.mail.utils import verify_mailgun_signature

def mailgun_view(func):
  def wrap(request, *args, **kwargs):
    token = request.POST.get('token', '')
    timestamp = request.POST.get('timestamp', '')
    signature = request.POST.get('signature', '')

    if verify_mailgun_signature(token, timestamp, signature):
      return func(request, *args, **kwargs)
    return HttpResponseForbidden()
  return csrf_exempt(wrap)
