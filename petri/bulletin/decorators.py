from django.conf import settings

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from petri.bulletin.models import Bulletin, Comment
from petri.chapter.decorators import chapter_view

def bulletin_view(*my_args, **my_kwargs):
    # unpack arguments (and assign defaults)
    leaders_only = my_kwargs.pop('leaders_only', False)
    owner_only = my_kwargs.pop('owner_only', False)
    leader_or_owner = my_kwargs.pop('leader_or_owner', False)
    cast = my_kwargs.pop('cast', True)

    def _bulletin_view(func):
        @chapter_view(*my_args, **my_kwargs)
        def wrap(request, *args, **kwargs):
            profile = None

            if request.user.is_authenticated() and request.user.is_active:
                profile = request.user.get_profile()

            request.bulletin = get_object_or_404(Bulletin, pk=kwargs.pop('bulletin'))
            is_owner = request.bulletin.owner == request.user
            is_leader = profile is not None and profile.is_leader
            is_mentee = profile is not None and is_leader and profile.has_mentee(request.bulletin.owner)
            can_moderate = is_leader and profile.can_moderate()
            if cast:
                request.bulletin = request.bulletin.cast()
            
            # moderators are "god" users - skip all validations
            if not can_moderate:
                # limit view to owner of content, if requested
                if not is_owner and (owner_only is True or owner_only == request.method):
                    return HttpResponseForbidden()
    
                # limit view to leaders (strictly), if requested
                if leaders_only and not is_leader:
                    return HttpResponseForbidden()
                
                # official bulletins only visible to leaders and owner
                if request.bulletin.is_official and not is_owner and not is_leader:
                    return HttpResponseForbidden()
                
                # leader-or-owner are only visible to owner or owner's leader
                if leader_or_owner and not is_owner and not is_mentee:
                    return HttpResponseForbidden()

            return func(request, *args, **kwargs)
        return wrap

    if len(my_args) == 1 and callable(my_args[0]):
        # No arguments, this is the decorator
        func, my_args = my_args[0], ()
        return _bulletin_view(func)
    
    # This is just returning the decorator
    return _bulletin_view


def comment_view(*my_args, **my_kwargs):
    # unpack arguments (and assign defaults)
    author_only = my_kwargs.pop('author_only', False)
    leader_or_author = my_kwargs.pop('leader_or_author', False)

    def _comment_view(func):
        @bulletin_view(*my_args, **my_kwargs)
        def wrap(request, *args, **kwargs):
            profile = None

            if request.user.is_authenticated() and request.user.is_active:
                profile = request.user.get_profile()
            
            request.comment = get_object_or_404(Comment, pk=kwargs.pop('comment'))
            author = request.comment.owner
            is_author = author == request.user
            is_leader = profile is not None and profile.is_leader
            is_mentee = profile is not None and is_leader and profile.has_mentee(author)
            can_moderate = profile is not None and profile.can_moderate()

            if not can_moderate:
                # limit view to author of comment, if requested
                if not is_author and (author_only is True or author_only == request.method):
                    return HttpResponseForbidden()

                if leader_or_author and not (is_mentee or is_author):
                    return HttpResponseForbidden()

            return func(request, *args, **kwargs)
        return wrap

    if len(my_args) == 1 and callable(my_args[0]):
        # No arguments, this is the decorator
        func, my_args = my_args[0], ()
        return _comment_view(func)
    
    # This is just returning the decorator
    return _comment_view
