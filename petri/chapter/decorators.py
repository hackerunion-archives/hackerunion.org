from urllib import urlencode

from django.conf import settings

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from django.template.loader import render_to_string

from petri.common.utils.auth import login_redirect

from petri.chapter.models import Chapter

def chapter_view(*my_args, **my_kwargs):
    """
    Provides authorization and authentication (as well as DB lookup) for chapter-based views.

    The logic implemented below is somewhat complex; what follows is a casual description of
    how everything should work.

    - If the user is not authenticated and the view is public, the user will be granted access.
    
    - If the user is not authenticated and the view is not public, the user will be prompted to login.

    The following tests occur for authenticated users, regardless of public status:

    - If a user is authenticated and in the "pending" state -- and pending is disallowed -- the user
    will be redirected to the pending status page.

    - If a user is authenticated and not a member -- and the view is members only -- the user will
    be redirected to their chapter page (if found); else, they'll be sent to the landing page.
    """

    # unpack arguments (and assign defaults)
    members_only = my_kwargs.pop('members_only', False)
    is_public = my_kwargs.pop('is_public', False)
    no_pending = my_kwargs.pop('no_pending', False)

    def _chapter_view(func):
        def wrap(request, *args, **kwargs):
            request.chapter = get_object_or_404(Chapter, slug=kwargs.pop('chapter', ''))
            request.is_member = False
            request.is_insider = False
            request.is_outsider = True

            if request.user.is_authenticated() and request.user.is_active:
                profile = request.user.get_profile()
            
                # obtain chapter and cache whether user is member or outsider (interpretation left to view)
                request.is_member = profile.is_member(request.chapter)
                request.is_insider = profile.is_insider()
                request.is_outsider = not request.is_insider

                # if current user is pending (and pending users disallowed), reroute
                if no_pending and profile.is_pending():
                    return HttpResponseRedirect(reverse('petri.account.views.pending'))
                
                # if current user is not a member (and non-members disallowed), reroute
                if not request.is_member and (members_only is True or members_only == request.method):
                    if request.has_chapter():
                        return HttpResponseRedirect(reverse('petri.chapter.views.home', kwargs={
                            'chapter': profile.chapter.slug
                        }))

                    return HttpResponseRedirect(reverse('petri.base.views.home'))
            
            elif not is_public:
                # not open to anonymous users -- attempt authentication
                return login_redirect(request)

            return func(request, *args, **kwargs)
        return wrap

    if len(my_args) == 1 and callable(my_args[0]):
        # No arguments, this is the decorator
        func, my_args = my_args[0], ()
        return _chapter_view(func)
    
    # This is just returning the decorator
    return _chapter_view
