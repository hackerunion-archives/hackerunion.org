from petri.petition.models import Petition
from django import forms


class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
