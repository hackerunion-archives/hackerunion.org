from django.db.models import signals
from petri.synergy.models import NotificationType


def create_notification_types(app, created_models, verbosity, **kwargs):
    # Proper Notifications
    NotificationType.objects.get_or_create(name="new_comment", email_subject='[Hacker Union] New Comment')
    NotificationType.objects.get_or_create(name="new_mention", email_subject='[Hacker Union] New Mention')
    NotificationType.objects.get_or_create(name="membership_approved", email_subject='[Hacker Union] You\'ve been accepted')
    NotificationType.objects.get_or_create(name="leadership_approved", email_subject='[Hacker Union] Your leadership request was approved')
    NotificationType.objects.get_or_create(name="new_leadership", email_subject='[Hacker Union] A new leadership request was created')
    NotificationType.objects.get_or_create(name="message", email_subject='[Hacker Union] New Message', send_individually=False)

    # Invitations
    NotificationType.objects.get_or_create(name="invite_site", email_subject="You've been invited to join Hacker Union")

signals.post_syncdb.connect(create_notification_types)
