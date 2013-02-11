import re
import urllib

from django.conf import settings

class BulletinRequest(object):
    # can be used in instances where a request is not handy
    def __init__(self, user, chapter, bulletin=None):
        self.user = user
        self.chapter = chapter
        self.bulletin = bulletin


def populate_request(request, user, chapter, bulletin=None):
    request.user = user
    request.chapter = chapter

    if bulletin:
        request.bulletin = bulletin

    return request


def get_mentions(content):
    return re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9_]+)', content)


def linkify_mentions(bulletin_or_comment):
    chapter = bulletin_or_comment.get_chapter()
    content = bulletin_or_comment.content

    def sub_helper(match):
        return r'<a href="http://' + settings.DOMAIN  + '/' + chapter.slug + '/members/?n=' + urllib.quote_plus(match.group(1).lower()) + '">' + match.group(1).lower() + '</a>'

    return re.sub(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9_]+)', sub_helper, content)
