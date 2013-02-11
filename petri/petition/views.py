from django.template import RequestContext
from petri.petition.forms import PetitionForm
from django.shortcuts import redirect, render_to_response


def home(request):
    if request.method == "POST":
        petition_form = PetitionForm(request.POST)
        if petition_form.is_valid():
            petition_form.save()
            return redirect('/petition/thanks/')

    else:
        petition_form = PetitionForm()

    return render_to_response('petition/home.jade',
                              {'petition_form': petition_form},
                              context_instance=RequestContext(request))


def thanks(request):
    return render_to_response('petition/thanks.jade',
                              {},
                              context_instance=RequestContext(request))
