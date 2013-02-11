import json
import hmac
import pprint
import urllib
import hashlib
import requests

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.html import strip_entities

from django.contrib.auth.models import User

from petri.chapter.models import Chapter
from petri.common.utils.string import random_string

CHAPTER_PREFIX = "[chapter]"
PROXY_PREFIX = "[proxy]"
DISCUSS_PREFIX = "[discuss]"
OFFICIAL_PREFIX = "[official]"
ANNOUNCE_PREFIX = "[announce]"

PROXY_FLAG = "%s:proxy:%s"
PROXY_FROM_FLAG = "%s:proxy:"
PROXY_TO_FLAG = "proxy:%s"

def _route_url(view, **kwargs):
    # www is essential here
    return "http://www.%s%s?%s" % (settings.DOMAIN, reverse(view), urllib.urlencode(kwargs))


class MailgunError(Exception):
    pass


class MailgunClientDebug(object):
    def __init__(self, *args, **kwargs):
        pass

    def __getattribute__(self, name):
        def _stub(*args, **kwargs):
            print "----- [stub] %s %s\n%s\n%s\n" % (name, "-" * (80 - len(name)), pprint.pformat(args), pprint.pformat(kwargs))
            return { "stub": True, "id": random_string()  }

        return _stub


class MailgunClientImpl():
    def __init__(self, silent=False):
        self._silent = silent
        self._access_key = settings.MAILGUN_ACCESS_KEY
        self._server_name = settings.MAILGUN_SERVER_NAME
        self._api_base = "https://api.mailgun.net/v2"
        self._api_url = "%s/%s" % (self._api_base, self._server_name)
    
    def _validate(self, r, json=False):
        if r.status_code != 200:
            if not self._silent:
                raise MailgunError(r)
            return None

        if not json:
            return r

        # avoid compatibility issues (sometimes json is a method, othertimes a dict)
        r = r.json() if callable(r.json) else r.json

        if r is None:
            if not self._silent:
                raise MailgunError("Couldn't parse json.")
            return None

        return r

    def list_routes(self, limit=100, skip=0):
        try:
            resp = requests.get("%s/routes" % self._api_base,
                auth=("api", self._access_key),
                data={ 'limit': limit, 
                       'skip': skip })
        except:
            if not self._silent:
                raise

            return None
        
        return self._validate(resp, json=True)

    def get_route(self, i):
        try:
            resp = requests.get("%s/routes/%s" % (self._api_base, i), auth=("api", self._access_key))
        except:
            if not self._silent:
                raise

            return None
        
        return self._validate(resp, json=True)

    def drop_route(self, i):
        try:
            resp = requests.delete("%s/routes/%s" % (self._api_base, i), auth=("api", self._access_key))
        except:
            if not self._silent:
                raise

            return False
        
        return self._validate(resp) is not None

    def drop_routes(self, contains=None, limit=500):
        routes = []
        total = None

        # ensure we're fetching all routes
        while total is None or total > 0:
            rts = self.list_routes(limit=limit)
            
            if total is None:
                total = rts.get("total_count", 0)
            
            routes.extend(rts.get('items', []))
            total -= len(rts.get('items', []))
        
        for route in routes:
            if route.get('id', None) and (contains is None or contains in route.get('description', '')):
                self.drop_route(route['id'])

    def create_route(self, expression, actions, priority=1, description="", prefix=""):
        try:
            resp = requests.post("%s/routes" % self._api_base,
                auth=("api", self._access_key),
                data={ 'priority': priority,
                       'description': ("%s %s" % (prefix, description)) if prefix else description,
                       'expression': expression,
                       'action': actions })
        except:
            if not self._silent:
                raise

            return False

        return self._validate(resp, json=True)

    def create_routes(self, routes, prefix=""):
        for route in routes:
            self.create_route(route[1], route[2], priority=route[0], description=route[3] if len(route) == 4 else "", prefix=prefix)
        
    def replace_routes(self, routes, contains=None, prefix=""):
        self.drop_routes(contains=contains)
        self.create_routes(routes, prefix=prefix)

    def list_lists(self, limit=100, skip=0):
        try:
            resp = requests.get("%s/lists" % self._api_base,
                auth=("api", self._access_key),
                data={ 'limit': limit, 
                       'skip': skip })
        except:
            if not self._silent:
                raise

            return None
        
        return self._validate(resp, json=True)

    def create_list(self, address, name="", description="", level="members", prefix=None):
        try:
            resp = requests.post("%s/lists" % self._api_base,
                auth=("api", self._access_key),
                data={ 'address': address,
                       'name': name or address,
                       'description': ("%s %s" % (prefix, description)) if prefix else description,
                       'access_level': level })
        except:
            if not self._silent:
                raise

            return False

        return self._validate(resp, json=True)
    
    def drop_list(self, address):
        try:
            resp = requests.delete("%s/lists/%s" % (self._api_base, address), auth=("api", self._access_key))
        except:
            if not self._silent:
                raise

            return False
        
        return self._validate(resp) is not None

    def drop_lists(self, contains=None, limit=500):
        lists = []
        total = None

        # ensure we're fetching all routes
        while total is None or total > 0:
            ls = self.list_lists(limit=limit)
            
            if total is None:
                total = ls.get("total_count", 0)
            
            lists.extend(ls.get('items', []))
            total -= len(ls.get('items', []))
        
        for lst in lists:
            if lst.get('address', None) and (contains is None or contains in lst.get('description', '')):
                self.drop_list(lst['address'])

    def list_membership(self, address, email, name="", subscribe=True, context={}):
        try:
            resp = requests.post("%s/lists/%s/members" % (self._api_base, address),
                auth=("api", self._access_key),
                data={ 'address': email,
                       'name': name,
                       'vars': json.dumps(context),
                       'subscribed': subscribe,
                       'upsert': True })
        except:
            if not self._silent:
                raise

            return False

        return self._validate(resp, json=True)

    def send_email(self, sender, to, text, html, subject="", cc=[], bcc=[], headers={}):
        try:
            data = { 'from': sender,
                     'to': ", ".join(to) if type(to) is list else to,
                     'subject': subject,
                     'text': text,
                     'html': html }
            
            for k, v in headers.iteritems():
                data["h:%s" % k] = v 

            if cc:
                data['cc'] = ", ".join(cc) if type(cc) is list else cc
            
            if bcc:
                data['bcc'] = ", ".join(bcc) if type(bcc) is list else bcc

            resp = requests.post("%s/messages" % self._api_url,
                auth=("api", self._access_key),
                data=data)

        except:
            if not self._silent:
                raise

            return False

        return self._validate(resp, json=True)


MailgunClient = MailgunClientDebug if settings.LOCAL else MailgunClientImpl


#
# Higher level mail tasks.
#


def verify_mailgun_signature(token, timestamp, signature):
    return signature == hmac.new(
                             key=settings.MAILGUN_ACCESS_KEY,
                             msg='{}{}'.format(timestamp, token),
                             digestmod=hashlib.sha256).hexdigest()


def proxy_email(email, alias, relative=False, silent=True, unproxy=True):
    c = MailgunClient(silent=silent)
    alias = "%s@%s" % (alias, settings.EMAIL_DOMAIN) if relative else alias
    
    if unproxy:
        unproxy_email(email, alias, relative=relative, silent=silent)

    return c.create_route(r'match_recipient("%s")' % alias,
        actions=[ r'forward("%s")' % email, r'stop()' ],
        priority=100,
        description= PROXY_FLAG % (email, alias),
        prefix=PROXY_PREFIX)


def unproxy_email(email, alias, relative=False, silent=True):
    c = MailgunClient(silent=silent)
    alias = "%s@%s" % (alias, settings.EMAIL_DOMAIN) if relative else alias
    
    return c.drop_routes(contains=PROXY_FROM_FLAG % email)


def create_chapter_routes(chapter, silent=True):
    c = MailgunClient(silent=silent)

    c.create_route(r'match_recipient("%s")' % chapter.get_discuss_list(),
        actions=[ r'forward("%s")' % _route_url("petri.mail.views.discuss", chapter=chapter.id), r'stop()' ],
        priority=10,
        description='%s discussion list' % chapter.slug,
        prefix=CHAPTER_PREFIX)

    c.create_route(r'match_recipient("%s")' % chapter.get_official_list(),
        actions=[ r'forward("%s")' % _route_url("petri.mail.views.official", chapter=chapter.id), r'stop()' ],
        priority=10,
        description='%s official list' % chapter.slug,
        prefix=CHAPTER_PREFIX)


def create_chapter_lists(chapter, silent=True):
    c = MailgunClient(silent=silent)

    c.create_list(chapter.get_announce_list(), description=chapter.slug, prefix=ANNOUNCE_PREFIX, level="readonly")
    c.create_list(chapter.get_official_list(), description=chapter.slug, prefix=OFFICIAL_PREFIX, level="members")
    c.create_list(chapter.get_discuss_list(), description=chapter.slug, prefix=DISCUSS_PREFIX, level="members")


def subscribe_list(lst, email, silent=True, welcome=True):
    c = MailgunClient(silent=silent)
    c.list_membership(lst, email, subscribe=True)
    
    if welcome:
        context = { 'list': lst, 'email': email, 'domain': settings.DOMAIN }
        send_email(email,
                   subject="Subscribed to %s" % lst,
                   text=render_to_string("notifications/subscribe_list/email_txt.jade", context),
                   body=render_to_string("notifications/subscribe_list/email.jade", context),
                   internal=True,
                   silent=silent)


def unsubscribe_list(lst, email, silent=True):
    c = MailgunClient(silent=silent)
    c.list_membership(lst, email, subscribe=False)


def send_email(to, subject="", text="", body="", sender=None, reply=None, internal=False, silent=True):
    c = MailgunClient(silent=silent)
    body = body or text
    text = text or strip_entities(strip_tags(body))
    headers = {}

    if internal:
        headers[settings.INTERNAL_EMAIL_HEADER] = "Made by MY team."

    if reply:
        headers["In-Reply-To"] = reply

    resp = c.send_email(sender or settings.DEFAULT_EMAIL, to, text, body, subject=subject, headers=headers)

    return resp.get("id", "")


def sync_lists(drop=True, silent=True):
    c = MailgunClient(silent=silent)

    # drop all lists, and drop all list routes
    c.drop_lists()
    c.drop_routes(contains=CHAPTER_PREFIX)
    
    for chapter in Chapter.objects.all():
        create_chapter_lists(chapter, silent=silent)
        create_chapter_routes(chapter, silent=silent)
        
        for profile in chapter.userprofile_set.all():
            if profile.allow_announce:
                subscribe_list(chapter.get_announce_list(), profile.get_email(proxy=False), silent=silent)
            
            if profile.allow_discuss:
                subscribe_list(chapter.get_discuss_list(), profile.get_email(proxy=False), silent=silent)

            if profile.allow_official and profile.is_leader:
                subscribe_list(chapter.get_official_list(), profile.get_email(proxy=False), silent=silent)


def sync_proxies(drop=True, silent=True):
    c = MailgunClient(silent=silent)
    c.drop_routes(contains=PROXY_PREFIX)
   
    for user in User.objects.exclude(email__isnull=True).exclude(email=""):
        proxy_email(user.email, user.username, relative=True, unproxy=False)


def sync_all(silent=True):
    sync_lists(silent=silent)
    sync_proxies(silent=silent)
