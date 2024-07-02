from django import forms
from .models import Gown, Certification

class GownFormReusable(forms.ModelForm):
    certificates = forms.ModelMultipleChoiceField(
        queryset=Certification.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Gown
        fields = ['reusable', 'weight', 'washes', 'cost', 'certificates']

class GownForm(forms.ModelForm):
    certificates = forms.ModelMultipleChoiceField(
        queryset=Certification.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Gown
        fields = ['reusable', 'weight', 'cost', 'certificates']


class GownSelectionForm(forms.Form):
    selected_gowns = forms.ModelMultipleChoiceField(
        queryset=Gown.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )