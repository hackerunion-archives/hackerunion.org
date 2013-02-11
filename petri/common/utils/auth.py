import urllib

from django.conf import settings
from django.contrib.auth.models import User

from django.http import HttpResponseRedirect

from petri.common.utils.string import random_string

def login_redirect(request):
    return HttpResponseRedirect("%s?%s" % (settings.LOGIN_URL, urllib.urlencode({ 'next': request.path })))


def create_user_without_username(password=None):
  user = User.objects.create_user(make_random_username(), '', password=password)

  # create a stub user if password blank
  if password is None:
    user.is_active = False
    user.save()

  return user


def make_random_username():
  while True:
    username = random_string(max_length=25)

    try:
      User.objects.get(username__iexact=username)
    except User.DoesNotExist:
      return username
