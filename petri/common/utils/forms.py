from django import forms

from django.core.validators import validate_email

from django.forms.fields import NullBooleanField
from django.forms.widgets import NullBooleanSelect

class MultipleEmailsField(forms.Field):
    def clean(self, value):
        """
        Check that the field contains one or more comma-separated emails
        and normalizes the data to a list of the email strings.
        """
        if not value:
            raise forms.ValidationError('Enter at least one e-mail address.')
        emails = [_.strip() for _ in value.split(',')]
        for email in emails:
            validate_email(email)

        # Always return the cleaned data.
        return emails


class SmartNullBooleanSelect(NullBooleanSelect):
    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        return {u'2': True,
                True: True,
                'true': True,
                'True': True,
                u'3': False,
                'false': False,
                'False': False,
                False: False}.get(value, None)


class SmartNullBooleanField(NullBooleanField):
    widget = SmartNullBooleanSelect

    def to_python(self, value):
        if value == 'true':
            value = 'True'

        if value == 'false':
            value = 'False'

        return super(SmartNullBooleanField, self).to_python(value)


class DeletionForm(forms.Form):
    delete = forms.BooleanField(initial=False, required=False)

    def is_delete(self):
        return self.cleaned_data.get('delete', False)

    def __init__(self, *args, **kwargs):
        data = kwargs.get('data', {})
        delete = data.get('delete') or False

        if delete: 
            kwargs['data'] = { 'delete': True }

        super(DeletionForm, self).__init__(*args, **kwargs)
        
        # ensure no field is required (to allow deletion)
        # must be invoked after above constructor
        if delete:
            for k in self.fields.iterkeys():
                self.fields[k].required = False
