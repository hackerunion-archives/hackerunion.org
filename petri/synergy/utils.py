from petri.talk.models import Talk
from petri.event.models import Event
from datetime import datetime
from django.template import Context
from petri import settings
from django.template.loader import get_template
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives


def create_and_send_email_digest(time_ago, to_user_profiles=[], subject="[Hacker Union] Digest"):
    '''
        time_ago is a timedelta object you
        best believe, buster. If you
        want a digest of the past day's activities,
        pass in timedelta(days=1), nahmsayin?


        Digest Algorithm
        ----------------

        1. Get all talks created in timeframe
        2. Get all talks with comments posted in timeframe
        3. The 'post set' = 1 union 2
        4. Get all events

    '''

    timeframe = datetime.now() - time_ago

    created_talks = Talk.objects.filter(Q(is_official=False) & (Q(created__gte=timeframe) | Q(comment__created_at__gte=timeframe))).distinct()
    created_events = Event.objects.filter(created__gte=timeframe).distinct()

    context_dict = {'talks': created_talks, 'events': created_events, 'domain': settings.DOMAIN, 'chapter': 'nyc'}
    context = Context(context_dict)

    from_email = settings.NOTIFICATION_EMAIL

    plaintext = get_template('notifications/summary/email_txt.jade')
    html = get_template('notifications/summary/email.jade')
    text_content = plaintext.render(context)
    html_content = html.render(context)

    for user in to_user_profiles:
        message = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=[user.get_email(proxy=False)])
        message.attach_alternative(html_content, "text/html")
        message.send()
