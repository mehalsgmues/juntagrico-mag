from django import forms
from django.utils.translation import gettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from mapjob.models import MapJob


class PickupLocationForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = MapJob
        fields = ['id', 'pickup_location']
        labels = {
            "pickup_location": _("Abholung in:")
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'mapjob:set_pickup_location'
        self.helper.form_class = 'form-inline'
        self.helper.label_class = 'my-1 mr-2'
        self.helper.field_class = 'my-1 mr-sm-2'
        self.helper.layout = Layout(
            'id',
            'pickup_location',
            Submit('submit', _('Ändern'), css_class='btn-success my-1'),
        )
