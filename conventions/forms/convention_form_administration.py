from django import forms
from django.core.validators import RegexValidator
from instructeurs.models import Administration


class UpdateConventionAdministrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        administrations_queryset = kwargs.pop("administrations_queryset")
        super().__init__(*args, **kwargs)
        self.fields["administration"].queryset = administrations_queryset

    administration = forms.ModelChoiceField(
        label="Administration",
        queryset=Administration.objects.all(),
        to_field_name="uuid",
        error_messages={
            "required": "Vous devez choisir une administration",
            "min_length": "min : Vous devez choisir une administration",
            "invalid_choice": "invalid : Vous devez choisir une administration",
        },
    )
