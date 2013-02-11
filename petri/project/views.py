from petri.chapter.decorators import chapter_view
from petri.bulletin.decorators import bulletin_view

from petri.project.forms import ProjectForm
from petri.project.models import Project
from petri.bulletin.forms import PromoteForm

from petri.talk.models import Talk
from petri.common.utils import json
from petri.common.decorators import jsonify
from django.shortcuts import redirect

from django.http import HttpResponseNotAllowed

from django.template import Context
from django.template.loader import get_template

from django.template import RequestContext

from django.shortcuts import render_to_response


@chapter_view
def projects(request):
    if request.method == 'POST':
        project_form = ProjectForm(request, request.POST)
        if project_form.is_valid():
            project = project_form.save()
            return redirect('/' + request.chapter.slug + '/posts/' + str(project.pk))
    else:
        project_form = ProjectForm(request)
    projects = Project.objects.filter(chapter=request.chapter).order_by('-created')

    return render_to_response('project/projects.jade',
                               {'projects': projects,
                                'project_form': project_form},
                               context_instance=RequestContext(request))    


@jsonify
@bulletin_view(leader_or_owner=True)
def edit_project(request):
    if request.method == 'POST':
        form = ProjectForm(request, data=request.POST)

        if form.is_valid():
            form.save(request.bulletin)
            projects = Project.objects.filter(chapter=request.chapter).order_by('-created')
            contextDict = {'projects': projects, 'current_user': request.user}
            context = Context(contextDict)

            template = get_template('project/projects.jade')
            return json.success({'feed': template.render(context)})
        
        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
