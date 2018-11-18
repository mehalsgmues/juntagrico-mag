from django.forms import *

from juntagrico_crowdfunding.models import Funder, Fund

class RegisterFunderForm(ModelForm):
    class Meta:
        model = Funder
        fields = ['first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location', 'phone']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'addr_street': TextInput(attrs={'class': 'form-control'}),
            'addr_zipcode': TextInput(attrs={'class': 'form-control'}),
            'addr_location': TextInput(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'})
        }


class FundForm(ModelForm):
    quantity = IntegerField()

    class Meta:
        model = Fund
        fields = ['sponsor', 'message', 'fundable']
        widgets = {
            'sponsor': TextInput(attrs={'class': 'form-control'}),
            'message': Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fundable': HiddenInput()
        }

    def __init__(self, max_quantity, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['quantity'] = IntegerField(
            label=u'Anzahl Einheiten',
            min_value=1,
            max_value=max_quantity,
            initial=1,
            widget=NumberInput(attrs={'class': 'form-control'})
        )
