from petri.common.utils import json
from petri.common.decorators import jsonify
from petri.synergy.forms import NewInvitation
from petri.synergy.models import Notification,NotificationDict
from petri.bulletin.models import Bulletin,Comment
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
        unread = Notification.objects.filter(users__in=[request.user.pk], status=Notification.UNREAD)
        jsonArr=[]
        for notif in unread.all():
          jsonDict = {}
          notifDict = NotificationDict.objects.filter(notification=notif)
          bull_id = int(getNDVal(notifDict,'bulletin'))
          comment_id = int(getNDVal(notifDict,'comment'))
          bull_title = Bulletin.objects.filter(id=bull_id).values('title')[0]['title']
          chapter_id = Bulletin.objects.filter(id=bull_id).values('chapter')[0]['chapter']
          raw_comm = Comment.objects.filter(id=comment_id).values('content')[0]['content']
          abbr_comm = strip_tags(raw_comm)[0:30]
         
          jsonDict['bulletin_id'] = bull_id
          jsonDict['bulletin_title'] = bull_title
          jsonDict['comment_id' ] = comment_id
          jsonDict['comment_str' ] = abbr_comm
          jsonDict['notif_id' ] = notif.id
          jsonArr.append(jsonDict)
        chapter = Chapter.objects.filter(id=chapter_id).values('slug')[0]['slug']
        retDict = {'notifs':jsonArr,'chapter':chapter}
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

def getNDVal(notifDict,inkey):
  for entry in notifDict:
    if entry.key == inkey:
      return entry.value
