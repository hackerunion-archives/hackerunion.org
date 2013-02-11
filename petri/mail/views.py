from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseBadRequest

from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from petri.common.utils import json
from petri.common.utils.debug import debug
from petri.common.decorators import jsonify

from petri.chapter.models import Chapter
from petri.bulletin.models import Bulletin

from petri.mail.decorators import mailgun_view

from petri.mail.forms import BroadcastMailForm
from petri.mail.forms import BroadcastOfficialForm

@mailgun_view
def discuss(request):
    if request.method == 'POST':
        form = BroadcastMailForm(data=request.REQUEST)

        if form.is_valid():
            form.save()

            return HttpResponse()
        
        debug(str(form.errors), system="mail-discuss")

        return HttpResponse(content=str(form.errors), content_type="text/html", status=406)
    return HttpResponseNotAllowed(['POST'])


@mailgun_view
def official(request):
    if request.method == 'POST':
        form = BroadcastOfficialForm(data=request.REQUEST)

        if form.is_valid():
            form.save()

            return HttpResponse()

        debug(str(form.errors), system="mail-official")

        return HttpResponse(content=str(form.errors), content_type="text/html", status=406)
    return HttpResponseNotAllowed(['POST'])
