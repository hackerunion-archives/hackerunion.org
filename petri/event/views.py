from petri.chapter.decorators import chapter_view
from petri.event.forms import EventForm
from petri.event.models import Event
from petri.common.decorators import jsonify
from petri.common.utils import json
from django.http import HttpResponseNotAllowed
from django.template import Context
from django.template.loader import get_template
from petri.bulletin.decorators import bulletin_view


@jsonify
@chapter_view
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            events = Event.objects.filter(chapter=request.chapter).order_by('-created')
            contextDict = {'events': events, 'current_user': request.user}
            context = Context(contextDict)

            template = get_template('event/events.jade')
            return json.success({'feed': template.render(context)})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])


@jsonify
@bulletin_view(leader_or_owner=True)
def edit_event(request):
    if request.method == 'POST':
        form = EventForm(request, data=request.POST)

        if form.is_valid():
            form.save(request.bulletin)
            events = Event.objects.filter(chapter=request.chapter).order_by('-created')
            contextDict = {'events': events, 'current_user': request.user}
            context = Context(contextDict)

            template = get_template('event/events.jade')
            return json.success({'feed': template.render(context)})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
