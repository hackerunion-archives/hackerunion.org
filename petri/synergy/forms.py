from django import forms
from petri.synergy.models import Invitation, NotificationType


class NewInvitation(forms.Form):
    to_email = forms.EmailField()
    comment_id = forms.IntegerField(required=False)
    annotation_id = forms.IntegerField(required=False)
    draft_id = forms.IntegerField(required=False)
    post_id = forms.IntegerField(required=False)

    def save(self):
	dataDict = {}
	if self.cleaned_data['comment_id']:
	    notification_type = NotificationType.objects.get(name="invite_comment")
	    dataDict["comment"] = self.cleaned_data['comment_id']
	elif self.cleaned_data['annotation_id']:
	    notification_type = NotificationType.objects.get(name="invite_annotation")
	    dataDict["annotation"] = self.cleaned_data['annotation_id']
	elif self.cleaned_data['draft_id']:
	    notification_type = NotificationType.objects.get(name="invite_draft")
	    dataDict["draft"] = self.cleaned_data['draft_id']
	elif self.cleaned_data['post_id']:
	    notification_type = NotificationType.objects.get(name="invite_post")
	    dataDict["post"] = self.cleaned_data['post_id']
	else:
	    notification_type = NotificationType.objects.get(name="invite_site")

	invitation = Invitation.objects.create(to_email=self.cleaned_data["to_email"], notification_type=notification_type)
	invitation.add_dictionary(dataDict)
	invitation.dispatch()

	return invitation
