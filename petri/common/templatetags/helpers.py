import re
import random
import datetime

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.template.defaultfilters import stringfilter

from petri.common.utils.dt import unixtime as unixtime_imp
from petri.common.utils.helpers import force
from petri.common.utils.string import shrink
from petri.common.utils.display import textcloud_scale
from django.template.loader import render_to_string
from django.utils.timezone import now


register = template.Library()

@register.filter
def can_edit(user, owner):
    if not (user.is_authenticated() and user.is_active):
        return False

    profile = user.get_profile()
    return user == owner or profile.can_moderate() or (profile.is_leader and owner.get_profile().leader == profile.user)


@register.filter
@stringfilter
def get_settings(value):
    return getattr(settings, value, '')


@register.filter
@stringfilter
def breakup(value, arg=" "):
    return arg.join(_ for _ in str(value))


@register.filter
def percent(value):
    return "%d%%" % (value * 100)


@register.filter
def unixtime(value):
    return str(unixtime_imp(value))


@register.filter
def attr(values, attr):
    return values.get(attr, None)

@register.filter(name='range')
@stringfilter
def _range(value):
    return range(int(value))


@register.filter(name='shrink')
@stringfilter
def _shrink(value, arg):
    args = arg.split(',')

    return shrink(value, int(args[0]), stupidify=('y' in args[1].lower() if len(args) > 1 else False))


@register.simple_tag
def cachebuster():
    return str(random.randint(1, 10000000))


@register.simple_tag(takes_context=True)
def render_bulletin_inline(context, bulletin, current_user_profile):
    return bulletin.render_inline(current_user_profile, context=context)


@register.simple_tag(takes_context=True)
def render_bulletin(context, bulletin, current_user_profile):
    return bulletin.render(current_user_profile, context=context)


@register.simple_tag
def render_member_card(user_profile, current_user_profile):
    return render_to_string("account/card.jade", {
        'card_user': user_profile,
        'current_user_profile': current_user_profile,
        'settings': settings
    })


@register.simple_tag
def following(bulletin, current_user):
    return "active" if (current_user in bulletin.followed_by.all()) else ""


@register.simple_tag
def humanize_time_diff(timestamp=None):
    """
    Returns a humanized string representing time difference
    between now() and the input timestamp.

    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """

    timeDiff = now() - timestamp
    days = timeDiff.days
    hours = timeDiff.seconds / 3600
    minutes = timeDiff.seconds % 3600 / 60
    seconds = timeDiff.seconds % 3600 % 60

    str = ""
    tStr = ""
    if days > 0:
        if days == 1:
            tStr = "day"
        else:
            tStr = "days"
        str = str + "%s %s ago" % (days, tStr)
        return str
    elif hours > 0:
        if hours == 1:
            tStr = "hour"
        else:
            tStr = "hours"
        str = str + "%s %s ago" % (hours, tStr)
        return str
    elif minutes > 0:
        if minutes == 1:
            tStr = "minute"
        else:
            tStr = "minutes"
        str = str + "%s %s ago" % (minutes, tStr)
        return str
    elif seconds > 0:
        if seconds == 1:
            tStr = "second"
        else:
            tStr = "seconds"
        str = str + "%s %s ago" % (seconds, tStr)
        return str
    else:
        return "Just Now"
