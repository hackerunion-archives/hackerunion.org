from petri.chapter.decorators import chapter_view
from petri.bulletin.decorators import bulletin_view
from petri.talk.forms import TalkForm
from petri.bulletin.forms import PromoteForm
from petri.talk.models import Talk
from petri.common.decorators import jsonify
from petri.common.utils import json
from django.http import HttpResponseNotAllowed
from django.template import Context
from django.template.loader import get_template


@jsonify
@chapter_view
def add_talk(request):
    if request.method == 'POST':
        form = TalkForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            if request.user.get_profile().is_leader:
                talks = Talk.objects.filter(chapter=request.chapter).order_by('-created')
            else:
                talks = Talk.objects.filter(chapter=request.chapter, is_official=False).order_by('-created')
            contextDict = {'talks': talks, 'current_user': request.user}
            context = Context(contextDict)

            template = get_template('talk/talks.jade')
            return json.success({'feed': template.render(context)})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])


@jsonify
@bulletin_view(leader_or_owner=True)
def edit_talk(request):
    if request.method == 'POST':
        form = TalkForm(request, data=request.POST)

        if form.is_valid():
            form.save(request.bulletin)
            talks = Talk.objects.filter(chapter=request.chapter).order_by('-created')
            contextDict = {'talks': talks, 'current_user': request.user}
            context = Context(contextDict)

            template = get_template('talk/talks.jade')
            return json.success({'feed': template.render(context)})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
