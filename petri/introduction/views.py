from petri.chapter.decorators import chapter_view
from petri.introduction.forms import IntroductionForm
from petri.introduction.models import Introduction
from petri.common.decorators import jsonify
from petri.common.utils import json
from django.http import HttpResponseNotAllowed
from django.template import Context
from django.template.loader import get_template
from petri.bulletin.decorators import bulletin_view


@jsonify
@chapter_view
def add_intro(request):
    if request.method == 'POST':
        form = IntroductionForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            intros = Introduction.objects.filter(chapter=request.chapter).order_by('-created')
            contextDict = {'intros': intros, 'current_user': request.user}
            context = Context(contextDict)

            template = get_template('introduction/intros.jade')
            return json.success({'feed': template.render(context)})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])


@jsonify
@bulletin_view(leader_or_owner=True)
def edit_intro(request):
    if request.method == 'POST':
        form = IntroductionForm(request, data=request.POST)

        if form.is_valid():
            form.save(request.bulletin)
            intros = Introduction.objects.filter(chapter=request.chapter).order_by('-created')
            contextDict = {'intros': intros, 'current_user': request.user}
            context = Context(contextDict)

            template = get_template('introduction/intros.jade')
            return json.success({'feed': template.render(context)})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
