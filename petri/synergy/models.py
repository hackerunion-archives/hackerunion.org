from django.db import models
from django.contrib.auth.models import User
from petri import settings
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


class NotificationType(models.Model):
    name = models.CharField(max_length=140)
    generates_email = models.BooleanField(default=True)
    email_subject = models.CharField(max_length=256, blank=True, default="")
    send_individually = models.BooleanField(default=True)


class AbstractNotification(models.Model):
    notification_type = models.ForeignKey(NotificationType)
    sender = models.EmailField(blank=True, null=True)

    def add_dictionary(self, dictionary):
        for key, value in dictionary.items():
            NotificationDict.objects.create(notification=self, key=key, value=value)

    def generate_message(self, contextDict, to_emails=None, to_users=None):
        to_emails = to_emails or []
        to_users = to_users or []

        if self.sender:
            from_email = self.sender
            for user in to_users:
                to_emails.append(user.get_profile().get_email())
            cc_header = {'Cc': ",".join([from_email])}
        else:
            from_email = settings.NOTIFICATION_EMAIL
            for user in to_users:
                to_emails.append(user.email)
            cc_header = {}

        from_email = self.sender or settings.NOTIFICATION_EMAIL
        context = Context(contextDict)
        subject = self.notification_type.email_subject

        plaintext = get_template('notifications/' + self.notification_type.name + '/email_txt.jade')
        html = get_template('notifications/' + self.notification_type.name + '/email.jade')
        text_content = plaintext.render(context)
        html_content = html.render(context)

        message = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=to_emails, headers=cc_header)
        message.attach_alternative(html_content, "text/html")
        return message

    def dispatch(self, to_email=None, users=None):
        if self.notification_type.generates_email:
            contextDict = {}
            for entry in NotificationDict.objects.filter(notification=self):
                contextDict[entry.key] = entry.value

            contextDict["domain"] = settings.DOMAIN

            if users:
                if self.notification_type.send_individually:
                    for user in users:
                        contextDict["user"] = user
                        message = self.generate_message(contextDict=contextDict, to_users=[user])
                        message.send()
                else:
                    message = self.generate_message(contextDict=contextDict, to_users=users)
                    message.send()
            elif to_email:
                message = self.generate_message(contextDict=contextDict, to_emails=[to_email])
                message.send()


class Notification(AbstractNotification):
    READ = 1
    CURRENT = 2
    UNREAD = 3
    STATUS_CHOICES = (
        (READ, 'Read'),
        (CURRENT, 'Current'),
        (UNREAD, 'Unread'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=UNREAD)
    users = models.ManyToManyField(User)

    def get_short_html(self):
        contextDict = {}
        for entry in NotificationDict.objects.filter(notification=self):
            contextDict[entry.key] = entry.value

        context = Context(contextDict)
        template = get_template('notifications/' + self.notification_type.name + '/short.jade')
        print template.render(context)
        return template.render(context)

    def dispatch(self):
        super(Notification, self).dispatch(users=self.users.all())


class Invitation(AbstractNotification):
    to_email = models.EmailField()

    def dispatch(self):
        super(Invitation, self).dispatch(to_email=self.to_email)


class NotificationDict(models.Model):
    notification = models.ForeignKey(AbstractNotification)
    key = models.CharField(max_length=140)
    value = models.TextField()


# class EmailMultiAlternativesCC(EmailMultiAlternatives):

#     def __init__(self, *args, **kwargs):
#         if 'cc' in kwargs:
#             self.cc = kwargs['cc']
#             del kwargs['cc']
#         EmailMultiAlternatives.__init__(self, *args, **kwargs)

#     def message(self):
#         msg = EmailMultiAlternatives.message(self)
#         if self.cc:
#             msg['Cc'] = ', '.join(self.cc)
#         return msg

#     def recipients(self):
#         l = EmailMultiAlternatives.recipients(self)
#         if self.cc:
#             return l + self.cc
#         return l
