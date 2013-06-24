from django.conf import settings

from django.http import HttpResponseRedirect
from django.http import HttpResponseNotAllowed

from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from petri.common.utils import json
from petri.common.decorators import jsonify

from petri.talk.models import Talk
from petri.event.models import Event
from petri.leadership.models import Leadership
from petri.introduction.models import Introduction

from petri.account.forms import InviteForm
from petri.account.models import UserProfile

from petri.chapter.models import Chapter
from petri.chapter.decorators import chapter_view

import datetime

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    chunks = []
    for i in range(0, len(l), n):
        chunks.append([{'mentee': mentee} for mentee in l[i:i + n]])
    return chunks


def render_sidebar(user, is_insider=True):
    mentees = user.get_profile().get_mentees() if is_insider else []
    contextDict = {
        'current_user': user
    }

    if user.get_profile().is_leader:
        pending_requests = []
    else:
        pending_requests = Leadership.objects.filter(owner=user, response=Leadership.PENDING).order_by('-created')

    mentee_chunks = []

    if mentees:
        mentee_chunks = chunks(mentees, 3)

    count = 0
    for chunk in mentee_chunks:
        count += 3
        for i in range(0, 3 - len(chunk)):
            chunk.append({'mentee': None})

    for i in range(0, (settings.MAX_MENTEES - count) / 3):
        mentee_chunks.append([{'mentee': None} for j in range(0, 3)])

    my_mentee_string = ",".join([mentee.user.username for mentee in mentees])
    contextDict['mentee_chunks'] = mentee_chunks
    contextDict['my_mentee_string'] = my_mentee_string
    contextDict['pending_requests'] = pending_requests
    contextDict['current_chapter'] = user.get_profile().chapter
    context = Context(contextDict)

    template = get_template('chapter/sidebar.jade')
    return template.render(context)


@chapter_view(is_public=True, no_pending=True)
def home(request):
    # while this is techically a "public" view, all unauthenticated users
    # are sent to the members page.
    if request.is_outsider:
        return HttpResponseRedirect(reverse('petri.members.views.members', kwargs={
            'chapter': request.chapter.slug
        }))

    if request.user.get_profile().is_leader:
        talks = Talk.objects.filter(chapter=request.chapter).order_by('-created')
        tasks = Leadership.objects.leader_requests().order_by('-created')
        pending_requests = []
    else:
        talks = Talk.objects.filter(chapter=request.chapter, is_official=False).order_by('-created')
        tasks = []
        pending_requests = Leadership.objects.filter(owner=request.user, response=Leadership.PENDING).order_by('-created')

    mentees = request.user.get_profile().get_mentees() if request.is_insider else []

    mentee_chunks = []

    if mentees:
        mentee_chunks = chunks(mentees, 3)

    count = 0
    for chunk in mentee_chunks:
        count += 3
        for i in range(0, 3 - len(chunk)):
            chunk.append({'mentee': None})

    for i in range(0, (settings.MAX_MENTEES - count) / 3):
        mentee_chunks.append([{'mentee': None} for j in range(0, 3)])

    my_mentee_string = ",".join([mentee.user.username for mentee in mentees])
    members = UserProfile.objects.filter(chapter=request.chapter, status=UserProfile.APPROVED)
    member_usernames = [m.user.username for m in members]

    return render_to_response('chapter/home.jade',
                              {'talks': talks[:settings.MAX_BULLETINS],
                               'tasks': tasks,
                               'mentee_chunks': mentee_chunks,
                               'member_usernames': member_usernames,
                               'my_mentee_string': my_mentee_string,
                               'pending_requests': pending_requests
                               },
                              context_instance=RequestContext(request))


@jsonify
@chapter_view(members_only=True)
def invite(request):
    if request.method == 'POST':
        form = InviteForm(request, data=request.POST)

        if form.is_valid():
            code = form.save()
            return json.success({ "code": code })

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
