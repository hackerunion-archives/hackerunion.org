from django.conf import settings

from django.http import HttpResponseNotAllowed

from django.template import Context
from django.template.loader import get_template

from petri.chapter.decorators import chapter_view
from petri.bulletin.decorators import bulletin_view

from petri.common.utils import json
from petri.common.decorators import jsonify

from petri.leadership.forms import LeadResignForm
from petri.leadership.forms import JoinRequestForm
from petri.leadership.forms import LeadRequestForm
from petri.leadership.forms import PairRequestForm
from petri.leadership.forms import HelpRequestForm
from petri.leadership.forms import CancelRequestForm
from petri.leadership.forms import PromoteRequestForm

from petri.leadership.forms import JoinResponseForm
from petri.leadership.forms import LeadResponseForm
from petri.leadership.forms import PairResponseForm
from petri.leadership.forms import HelpResponseForm
from petri.leadership.forms import PromoteResponseForm

from petri.chapter.views import chunks
from petri.leadership.models import Leadership

#
# Utilities
#

def _request_view(formcls):
    @jsonify
    @chapter_view(members_only=True)
    def _inner(request):
        if request.method == 'POST':
            form = formcls(request, data=request.POST)
            if form.is_valid():
                form.save()

                contextDict = {'current_user': request.user}
                mentees = request.user.get_profile().get_mentees() if request.is_insider else []

                if request.user.get_profile().is_leader:
                    pending_requests = []
                else:
                    pending_requests = Leadership.objects.filter(owner=request.user, response=Leadership.PENDING).order_by('-created')

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
                contextDict['current_chapter'] = request.chapter
                context = Context(contextDict)

                template = get_template('chapter/sidebar.jade')
                return json.success({'sidebar': template.render(context)})

            return json.error(form.errors)
        return HttpResponseNotAllowed(['POST'])

    return _inner


def _response_view(formcls):
    @jsonify
    @bulletin_view(leaders_only=True)
    def _inner(request):
        if request.method == 'POST':
            form = formcls(request, data=request.POST)

            if form.is_valid():
                form.save()
                contextDict = {'current_user': request.user}
                mentees = request.user.get_profile().get_mentees() if request.is_insider else []

                if request.user.get_profile().is_leader:
                    pending_requests = []
                else:
                    pending_requests = Leadership.objects.filter(owner=request.user, response=Leadership.PENDING).order_by('-created')

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
                contextDict['current_chapter'] = request.chapter
                context = Context(contextDict)

                template = get_template('chapter/sidebar.jade')
                return json.success({'sidebar': template.render(context)})

            return json.error(form.errors)
        return HttpResponseNotAllowed(['POST'])

    return _inner

#
# Request views
#

join_request = _request_view(JoinRequestForm)
volunteer_request = _request_view(LeadRequestForm)
pair_request = _request_view(PairRequestForm)
help_request = _request_view(HelpRequestForm)
promote_request = _request_view(PromoteRequestForm)

#
# Response views
#

join_response = _response_view(JoinResponseForm)
volunteer_response = _response_view(LeadResponseForm)
pair_response = _response_view(PairResponseForm)
help_response = _response_view(HelpResponseForm)
promote_response = _response_view(PromoteResponseForm)

#
# Views
#

@jsonify
@bulletin_view(owner_only=True)
def cancel(request):
    if request.method == 'POST':
        form = CancelRequestForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            return json.success({})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])


@jsonify
@chapter_view(members_only=True)
def resign(request):
    if request.method == 'POST':
        form = LeadResignForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            return json.success({})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
