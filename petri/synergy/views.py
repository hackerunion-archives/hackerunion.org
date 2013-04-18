from petri.common.utils import json
from petri.common.decorators import jsonify
from petri.synergy.forms import NewInvitation
from petri.synergy.models import Notification, NotificationDict
from petri.bulletin.models import Bulletin, Comment
from petri.chapter.models import Chapter

from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.db import models
from django.shortcuts import redirect


@jsonify
@login_required
def get(request):
    if request.method == 'GET':
        notifications = Notification.objects.filter(users__in=[request.user.pk], status=Notification.UNREAD)
        chapter_id = request.user.get_profile().chapter.pk

        notification_array = []
        for notification in notifications.all():
            notification_dict = {}
            notification_values = NotificationDict.objects.filter(notification=notification)

            bulletin_id = getNDVal(notification_values, 'bulletin')
            bulletin_id = bulletin_id if bulletin_id is None else int(bulletin_id)

            if bulletin_id is None:
                continue

            comment_id = getNDVal(notification_values, 'comment')
            comment_id = comment_id if comment_id is None else int(comment_id)
            bulletin = Bulletin.objects.filter(id=bulletin_id)[0]

            bulletin_title = bulletin.title

            if comment_id is not None:
                raw_comment = Comment.objects.filter(id=comment_id).values('content')[0]['content']
                safe_comment = strip_tags(raw_comment)[0:30]
                notification_dict['comment_id'] = comment_id
                notification_dict['comment_str'] = safe_comment

            notification_dict['bulletin_id'] = bulletin_id
            notification_dict['bulletin_title'] = bulletin_title
            notification_dict['notif_id'] = notification.id
            notification_array.append(notification_dict)

        chapter = Chapter.objects.filter(id=chapter_id).values('slug')[0]['slug']
        retDict = {'notifs': notification_array, 'chapter': chapter}
        return json.success(retDict)

    return HttpResponseNotAllowed(['POST'])


@login_required
def read(request):
    redir_url = request.GET['url']
    notif_id = request.GET['notif_id']
    notif = Notification.objects.filter(id=notif_id)
    notif.update(status=Notification.READ)
    return redirect(redir_url)


@jsonify
def invite(request):
    if request.method == 'POST':
        form = NewInvitation(data=request.POST)

        if form.is_valid():
            form.save()
            return json.success()

    return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])


def getNDVal(notifDict, inkey):
    for entry in notifDict:
        if entry.key == inkey:
            return entry.value
    return None
