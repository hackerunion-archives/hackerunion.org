# from urllib import urlencode

# from django.conf import settings
from django.template import RequestContext

# from django.http import Http404
# from django.http import HttpResponse
from django.http import HttpResponseRedirect
# from django.http import HttpResponseNotAllowed

# from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import redirect

# from petri.common.decorators import jsonify

# from petri.common.utils import json
# from petri.common.utils.views import paginate
# from petri.common.utils.string import force_int
from petri.talk.models import Talk

from petri.chapter.models import Chapter
from petri.account.models import UserProfile
from petri.account.forms import FrontpageApplyForm


@ensure_csrf_cookie
def home(request):
    if request.user.is_authenticated() and request.user.is_active:
        profile = request.user.get_profile()

        # if user is authenticated and has a chapter, redirect to chapter home (which may send to pending page)
        if profile.has_chapter():
            return HttpResponseRedirect(reverse('petri.chapter.views.home', kwargs={
                'chapter': profile.chapter.slug
            }))

    if request.method == "POST":
        form = FrontpageApplyForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            request.session['apply_username'] = data['username']
            request.session['apply_email'] = data['email']
            request.session['apply_password'] = data['password']
            return redirect('/accounts/apply')

    else:
        form = FrontpageApplyForm()
    return render_to_response('home.jade',
                            {'form': form,
                             'current_user': request.user },
                            context_instance=RequestContext(request))


def chapters(request):
    chapters = Chapter.objects.all()
    return render_to_response('chapter/chapters.jade',
                              {'chapters': chapters},
                              context_instance=RequestContext(request))
