from django.template import RequestContext

from django.shortcuts import render_to_response
from petri.chapter.decorators import chapter_view
from petri.account.models import UserProfile
from petri.tag.models import Skill, Affiliation, Initiative


@chapter_view(is_public=True)
def members(request):

    if request.user.is_active and request.user.is_authenticated() and request.user.get_profile().is_insider():
        members = UserProfile.objects.filter(chapter=request.chapter, status=UserProfile.APPROVED)
    else:
        members = UserProfile.objects.filter(chapter=request.chapter, status=UserProfile.APPROVED, is_leader=True)
    skills = [skill.name for skill in Skill.objects.all()]
    affiliations = [a.name for a in Affiliation.objects.all()]
    initiatives = [i.name for i in Initiative.objects.all()]
    member_usernames = [m.user.username for m in members]

    return render_to_response('members/members.jade',
                               {'members': members,
                                'skills': skills,
                                'affiliations': affiliations,
                                'iniatives': initiatives,
                                'member_usernames': member_usernames},
                               context_instance=RequestContext(request))
