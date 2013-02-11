from django.conf import settings as django_settings
from petri.synergy.models import Notification


def settings(request):
    return {'settings': django_settings}


# NOTE: you can use request.* or current_* to access these pieces of data (in views that support these features)
def current_entities(request):
    return { 'is_member': getattr(request, 'is_member', False),
             'is_insider': getattr(request, 'is_insider', False),
             'is_outsider': getattr(request, 'is_outsider', False),
             'current_user': request.user,
             'current_chapter': getattr(request, 'chapter', request.user.get_profile().chapter if (request.user.is_authenticated() and request.user.is_active) else None),
             'current_bulletin': getattr(request, 'bulletin', None),
             'current_comment': getattr(request, 'comment', None)  }
