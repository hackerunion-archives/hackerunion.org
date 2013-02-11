from petri.pending.forms import PendingForm
from petri.pending.models import Pending
from petri.common.decorators import jsonify
from petri.common.utils import json
from django.http import HttpResponseNotAllowed
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required


@jsonify
@login_required
def add_pending(request):
    if request.method == 'POST' and request.user.get_profile().chapter:
        form = PendingForm(request, data=request.POST)

        if form.is_valid():
            form.save()
            pending = Pending.objects.filter(chapter=request.chapter).order_by('-created')
            contextDict = {'pendings': pending}
            context = Context(contextDict)

            template = get_template('pending/pendings.jade')
            return json.success({'feed': template.render(context)})

        return json.error(form.errors)
    return HttpResponseNotAllowed(['POST'])
