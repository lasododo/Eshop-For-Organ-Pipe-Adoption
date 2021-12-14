from django import forms

from .models import Address


class AddressForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)

        self.fields['address_line_1'] = forms.CharField(required=True, max_length=120, widget=forms.TextInput(attrs={
            'type': "text",
            'class': "form-control",
            'placeholder': "Address Line 1"
        }), label='')

        self.fields['address_line_2'] = forms.CharField(required=False, max_length=120, widget=forms.TextInput(attrs={
            'type': "text",
            'class': "form-control",
            'placeholder': "Address Line 2"
        }), label='')

        self.fields['city'] = forms.CharField(required=True, max_length=120, widget=forms.TextInput(attrs={
            'type': "text",
            'class': "form-control",
            'placeholder': "City"
        }), label='')

        self.fields['country'] = forms.CharField(required=True, max_length=120, widget=forms.TextInput(attrs={
            'type': "text",
            'class': "form-control",
            'placeholder': "Country"
        }), label='')

        self.fields['state'] = forms.CharField(required=True, max_length=120, widget=forms.TextInput(attrs={
            'type': "text",
            'class': "form-control",
            'placeholder': "State"
        }), label='')

        self.fields['postal_code'] = forms.CharField(required=True, widget=forms.NumberInput(attrs={
            'type': "number",
            'class': "form-control",
            'placeholder': "Postal Code",
            'min': '0'
        }), label='')

    class Meta:
        model = Address
        fields = [
            'address_line_1',
            'address_line_2',
            'city',
            'country',
            'state',
            'postal_code'
        ]
