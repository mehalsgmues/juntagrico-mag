from crispy_forms.bootstrap import FormActions
from django import forms
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.translation import gettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from mapjob.models import MapJob, PickupLocation


class InlineFormHelper(FormHelper):
    form_class = 'form-inline'
    label_class = 'my-1 mr-2'
    field_class = 'my-1 mr-sm-2'


class HorizontalFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-md-3'
    field_class = 'col-md-9'


class AllPickupLocationForm(forms.Form):
    pickup_location = forms.ModelChoiceField(queryset=PickupLocation.objects,
                                             label=_("Ich möchte alle meine Flyer hier holen:"))

    form_action_url = 'mapjob:set_all_pickup_location'
    text = {
        'submit': _('Ändern')
    }

    def __init__(self, *args, member=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.member = member
        self.helper = InlineFormHelper()
        self.helper.form_action = self.form_action_url
        self.helper.layout = Layout(
            'pickup_location',
            Submit('submit', self.text['submit'], css_class='btn-success my-1'),
        )

    def save(self):
        return MapJob.objects.of_member(self.member).need_pickup().update(
            pickup_location=self.cleaned_data['pickup_location']
        )


class PickupLocationForm(forms.ModelForm):
    form_action_url = 'mapjob:set_job_pickup_location'
    text = {
        'label': _("Abholung in:"),
        'submit': _('Ändern')
    }

    class Meta:
        model = MapJob
        fields = ['id', 'pickup_location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pickup_location'].label = self.text['label']
        self.helper = InlineFormHelper()
        self.helper.form_action = reverse(self.form_action_url, args=[self.instance.id])
        self.helper.layout = Layout(
            'pickup_location',
            Submit('submit', self.text['submit'], css_class='btn-success my-1'),
        )


class PickupForm(forms.Form):
    pickup_location = forms.ModelChoiceField(queryset=PickupLocation.objects,
                                             label=_('Abholort'), empty_label=_('Woanders'))
    for_jobs = forms.ModelMultipleChoiceField(queryset=MapJob.objects.none(),
                                              label=_('Ich habe die Flyer für diese Gebiete geholt'),
                                              help_text=_('Das kannst du später nochmal ändern, '
                                                          'wenn du nicht sicher bist, wo du die Flyer verteilst'),
                                              widget=forms.CheckboxSelectMultiple())
    amount = forms.IntegerField(label=_("Anzahl"), validators=[MinValueValidator(0)], initial=1000)

    form_action_url = 'mapjob:pickup'
    text = {
        'submit': _('Abgeholt')
    }

    def __init__(self, jobs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['for_jobs'].queryset = jobs
        first_location = jobs.first().pickup_location
        self.fields['pickup_location'].initial = first_location
        initial_jobs = jobs.filter(pickup_location=first_location)
        self.fields['for_jobs'].initial = initial_jobs
        self.fields['amount'].initial = initial_jobs.count()*1000
        if jobs.count() <= 1:
            self.fields['for_jobs'].widget = forms.MultipleHiddenInput()
        self.helper = HorizontalFormHelper()
        self.helper.form_action = self.form_action_url
        self.helper.layout = Layout(
            'pickup_location',
            'for_jobs',
            'amount',
            FormActions(Submit('submit', self.text['submit'], css_class='btn-success'))
        )

    def save(self):
        pickup_location = self.cleaned_data['pickup_location']
        pickup_location.available_flyers -= self.cleaned_data['amount']
        pickup_location.save()
        return self.cleaned_data['for_jobs'].update(pickup_location=pickup_location, progress=MapJob.Progress.PICKED_UP)
