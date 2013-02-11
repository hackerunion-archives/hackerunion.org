from petri.leadership.models import Leadership

from petri.leadership.forms import PairRequestForm
from petri.leadership.forms import JoinRequestForm
from petri.leadership.forms import PromoteRequestForm

from petri.bulletin.utils import BulletinRequest
from petri.bulletin.utils import populate_request

# These helper functions wrap the forms to allow requests to be generated
# programmatically. All request forms are written to accept the limited
# "BulletinRequest" instead of a pure HttpRequest.


def bootstrap_join_request(user, chapter, application, request=None):
    # need to populate the request since user hasn't authenticated yet
    request = populate_request(request, user, chapter) if request else BulletinRequest(user, chapter)
    form = JoinRequestForm(request, data={
        "content": application
    })

    if form.is_valid():
        form.save()
        return True

    return False


def create_promote_request(user, chapter, bulletin, request=None):
    request = request or BulletinRequest(user, chapter, bulletin)

    form = PromoteRequestForm(request, data={
        "related": bulletin.id,
        "content": bulletin.content
    })

    if form.is_valid():
        form.save()
        return True

    return False


def create_pair_request(user, chapter, reason, request=None):
    request = request or BulletinRequest(user, chapter)

    form = PairRequestForm(request, data={
        "content": reason
    })

    if form.is_valid():
        form.save()
        return True

    return False
