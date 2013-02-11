import re

from urllib import urlencode

from django.conf import settings
from django.template import RequestContext

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotAllowed

from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404, redirect
from petri.common.decorators import jsonify

from petri.common.utils import json
from petri.common.utils.views import paginate
from petri.common.utils.string import force_int

from petri.account.models import UserProfile

from petri.bulletin.decorators import bulletin_view, comment_view
from petri.bulletin.forms import CommentForm, PromoteForm, FollowForm

from petri.chapter.decorators import chapter_view

from petri.bulletin.models import Comment
from petri.bulletin.models import Bulletin


def alias(request, chapter, alias, index=0):
    # TODO: actually compute slugs and use those
    index = force_int(index)
    bulletin = Bulletin.objects.filter(title__iregex=r'^%s' % (re.escape(alias).replace('\-', '.')))

    if index >= len(bulletin):
        raise Http404

    return HttpResponseRedirect(reverse('petri.bulletin.views.home', kwargs={ 'chapter': chapter, 'bulletin': bulletin[index].pk }))


@bulletin_view(is_public=True)
def home(request):
    comments = request.bulletin.comment_set.all().order_by('-created_at')
    template_name = request.bulletin.override_template() or 'bulletin/bulletin.jade'
    mentees = request.user.get_profile().get_mentees() if request.is_insider else []
    my_mentee_string = ",".join([mentee.user.username for mentee in mentees])
    members = UserProfile.objects.filter(chapter=request.chapter, status=UserProfile.APPROVED)
    member_usernames = [m.user.username for m in members] if request.is_insider else []

    return render_to_response(template_name,
                              {'bulletin': request.bulletin,
                               'my_mentee_string': my_mentee_string,
                               'member_usernames': member_usernames,
                               'comments': comments},
                              context_instance=RequestContext(request))


@jsonify
@bulletin_view
def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            comments = request.bulletin.comment_set.all().order_by('-created_at')
            return json.success({'feed': render_to_string('comment/comments.jade', {'comments': comments, 'current_user': request.user, 'current_chapter': request.chapter})})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])


@comment_view(leader_or_author=True)
def delete_comment(request):
    # request authorized by decorator
    request.comment.delete()

    return redirect('/' + request.chapter.slug + '/posts/' + str(request.bulletin.pk) + '/')


@jsonify
@bulletin_view
def promote_bulletin(request):
    if request.method == 'POST':
        form = PromoteForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            return json.success()

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])


@jsonify
@bulletin_view
def follow_bulletin(request):
    if request.method == 'POST':
        form = FollowForm(request, data=request.POST)

        if form.is_valid():
            followed = form.save()
            return json.success({'followed': followed, 'id': request.user.pk, 'username': request.user.username, 'url': render_to_string('account/gravatar_img.jade', {'user': request.user})})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
