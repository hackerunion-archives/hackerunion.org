from PIL import Image as PImage

from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.views.decorators.csrf import ensure_csrf_cookie

from django.http import HttpResponse
from django.http import HttpResponseRedirect
# from django.conf import settings
from django.core.files import File

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.template import Context
from django.template.loader import get_template

from petri.account.forms import AccountApplicationForm, AccountEmailForm, AccountSocialForm, AccountSkillForm, InviteForm, AbandonForm, BanForm, NoticeForm, ModeratorForm, GuideForm, MarkupForm, TransferForm
from petri.chapter.models import Chapter
from petri.pending.models import Pending
from petri.leadership.models import Leadership
from petri.tag.models import Skill, Affiliation
from django.contrib.auth.decorators import login_required
from petri.common.decorators import jsonify
from petri.common.utils import json
from petri.leadership.forms import LeadResignForm
from django.http import HttpResponseNotAllowed
from petri.account.models import Invitation
from petri.synergy.models import Notification, NotificationType

from petri.chapter.views import render_sidebar

@login_required
def pending(request):
    profile = request.user.get_profile()

    # only pending and leaders may see this page
    if not profile.is_pending() and not profile.is_leader:
        return HttpResponseRedirect(reverse('petri.chapter.views.home', kwargs={
            'chapter': profile.chapter.slug
        }))

    current_chapter = profile.chapter
    pendings = Pending.objects.filter(chapter=current_chapter).order_by('-created')

    try:
        pending_bulletin = Leadership.objects.get(owner=request.user, request=Leadership.JOIN)
    except Leadership.DoesNotExist:
        pending_bulletin = None

    return render_to_response('account/pending.jade',
                              {'current_chapter': current_chapter,
                               'pendings': pendings,
                               'pending_bulletin': pending_bulletin},
                              context_instance=RequestContext(request))


@login_required
def settings(request):
    social_form = AccountSocialForm()
    email_form = AccountEmailForm()

    skills = [s.name for s in Skill.objects.all()]
    affiliations = [a.name for a in Affiliation.objects.all()]
    my_skill_string = ",".join([skill.name for skill in request.user.get_profile().skills.all()])
    my_affiliation_string = ",".join([affiliation.name for affiliation in request.user.get_profile().affiliations.all()])

    return render_to_response('account/set.jade',
                              {'social_form': social_form,
                               'email_form': email_form,
                               'skills': skills,
                               'affiliations': affiliations,
                               'is_insider': True,
                               'my_skill_string': my_skill_string,
                               'my_affiliation_string': my_affiliation_string},
                              context_instance=RequestContext(request))


@login_required
def settings_email(request):
    if request.method == "POST":
        email_form = AccountEmailForm(request.POST)
        if email_form.is_valid():
            email_form.save(request.user.get_profile())
            return redirect('/accounts/settings')
        else:
            return settings(request)

    return HttpResponseNotAllowed(['POST'])


@login_required
def settings_social(request):
    if request.method == "POST":
        social_form = AccountSocialForm(request.POST)
        if social_form.is_valid():
            social_form.save(request.user.get_profile())
            return redirect('/accounts/settings')
        else:
            return settings(request)

    return HttpResponseNotAllowed(['POST'])


@login_required
def settings_skill(request):
    if request.method == "POST":
        skill_form = AccountSkillForm(request.POST)
        if skill_form.is_valid():
            skill_form.save(request.user.get_profile())
            return redirect('/accounts/settings')
        else:
            return settings(request)

    return HttpResponseNotAllowed(['POST'])


@login_required
def settings_resign(request):
    if request.method == "POST":
        resign_form = LeadResignForm(request, data=request.POST)
        if resign_form.is_valid():
            resign_form.save(request.user.get_profile())
            return redirect('/accounts/settings')
        else:
            return settings(request)

    return HttpResponseNotAllowed(['POST'])


@login_required
@jsonify
def guide(request):
    if request.method == 'POST':
        data = request.POST
        if int(data['remove']) == 1:
            request.user.get_profile().show_guide = False
        else:
            request.user.get_profile().show_guide = True
        request.user.get_profile().save()
        return json.success()

    return HttpResponseNotAllowed(['POST'])


def apply(request, invite=None):
    init_pass = ""
    if request.method == 'POST':

        form = AccountApplicationForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
            return redirect("/")

    else:
        initial = {}
        if request.session.get('apply_username', None):
            initial['display_name'] = request.session['apply_username']

        if request.session.get('apply_email', None):
            initial['email'] = request.session['apply_email']

        if request.session.get('apply_password', None):
            init_pass = request.session['apply_password']

        if invite:
            try:
                invitation = Invitation.objects.get(code=invite)
                initial['invitation_code'] = invite
                initial['chapter'] = invitation.chapter.pk
                initial['email'] = invitation.target
            except Invitation.DoesNotExist:
                invite = None

        form = AccountApplicationForm(request, initial=initial)

    chapters = Chapter.objects.all()
    return render_to_response('account/apply.jade',
                              {"form": form, "init_pass": init_pass, "chapters": chapters, "invite": invite},
                              context_instance=RequestContext(request))


@login_required
@jsonify
def invite(request):
    if request.method == "POST":
        invite_form = InviteForm(request, data=request.POST)
        if invite_form.is_valid():
            invite_form.save()
            return json.success()

        return json.error(invite_form.errors)
    return HttpResponseNotAllowed(['POST'])


@login_required
@jsonify
def abandon(request):
    if request.method == "POST":
        abandon_form = AbandonForm(request, data=request.POST)
        if abandon_form.is_valid():
            abandon_form.save()
            return json.success({ 'sidebar': render_sidebar(request.user) })

        return json.error(abandon_form.errors)
    return HttpResponseNotAllowed(['POST'])


@login_required
@jsonify
def ban(request):
    if request.method == "POST":
        ban_form = BanForm(request, data=request.POST)
        if ban_form.is_valid():
            ban_form.save()
            return json.success({ 'sidebar': render_sidebar(request.user) })

        return json.error(ban_form.errors)
    return HttpResponseNotAllowed(['POST'])


@login_required
@jsonify
def moderator(request):
    if request.method == "POST":
        moderator_form = ModeratorForm(request, data=request.POST)
        if moderator_form.is_valid():
            moderator_form.save()
            return json.success({ 'sidebar': render_sidebar(request.user) })

        return json.error(moderator_form.errors)
    return HttpResponseNotAllowed(['POST'])


@login_required
@jsonify
def guide(request):
    if request.method == "POST":
        guide_form = GuideForm(request, data=request.POST)
        if guide_form.is_valid():
            guide_form.save()
            return json.success({ 'sidebar': render_sidebar(request.user) })

        return json.error(guide_form.errors)
    return HttpResponseNotAllowed(['POST'])


@login_required
@jsonify
def markup(request):
    if request.method == "POST":
        markup_form = MarkupForm(request, data=request.POST)
        if markup_form.is_valid():
            markup_form.save()
            return json.success({ 'sidebar': render_sidebar(request.user) })

        return json.error(markup_form.errors)
    return HttpResponseNotAllowed(['POST'])

@login_required
@jsonify
def transfer(request):
    if request.method == "POST":
        transfer_form = TransferForm(request, data=request.POST)
        if transfer_form.is_valid():
            transfer_form.save()
            return json.success({ 'sidebar': render_sidebar(request.user) })

        return json.error(transfer_form.errors)
    return HttpResponseNotAllowed(['POST'])


@login_required
@jsonify
def settings_notice(request):
    if request.method == "POST":
        notice_form = NoticeForm(request, data=request.POST)
        if notice_form.is_valid():
            notice_form.save()
            return json.success()

        return json.error(notice_form.errors)
    return HttpResponseNotAllowed(['POST'])


def reset_thanks(request):
    return render_to_response('account/reset-thanks.jade',
                              {},
                              context_instance=RequestContext(request))


@jsonify
def message(request):
    if request.method == 'POST':
        data = request.POST

        valid = True
        recipients = []

        for recipient in data.getlist("to"):
            try:
                user = User.objects.get(username=recipient)
            except User.DoesNotExist:
                continue

            if not request.user.is_authenticated() or not request.user.is_active:
                if not user.get_profile().is_leader:
                    valid = False

            if not valid:
                return json.errors({"Message": "You are not Allowed to do that!"})

            recipients.append(user)

        notification_type = NotificationType.objects.get(name="message")
        if request.user.is_authenticated() and request.user.is_active:
            notification = Notification(notification_type=notification_type, sender=request.user.get_profile().get_email())
        else:
            notification = Notification(notification_type=notification_type, sender=data.get("from"))
        notification.save()
        for recipient in recipients:
            notification.users.add(recipient)

        if request.user.is_authenticated() and request.user.is_active:
            notification.add_dictionary({"message": data['message'], "sender_display_name": request.user.get_profile().display_name, "sender_username": request.user.username})
        else:
            notification.add_dictionary({"message": data['message'], "sender_display_name": data.get('from'), "sender_username": request.user.username})
        notification.save()
        notification.dispatch()

        return json.success()

    return HttpResponseNotAllowed(['POST'])
