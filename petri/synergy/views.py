from petri.common.utils import json
from petri.common.decorators import jsonify
from petri.synergy.forms import NewInvitation
from petri.synergy.models import Notification

from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required


@jsonify
@login_required
def read(request):
    if request.method == 'POST':
        unread = Notification.objects.filter(users__in=[request.user.pk], status=Notification.UNREAD).count()
        if unread > 0:
            Notification.objects.filter(users__in=[request.user.pk], status=Notification.CURRENT).update(status=Notification.READ)
            Notification.objects.filter(users__in=[request.user.pk], status=Notification.UNREAD).update(status=Notification.CURRENT)
        print json.success()
        return json.success()

    return HttpResponseNotAllowed(['POST'])


@jsonify
def invite(request):
    if request.method == 'POST':
        form = NewInvitation(data=request.POST)

        if form.is_valid():
            form.save()
            return json.success()

    return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
