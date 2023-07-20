from django import forms
from django.core.validators import RegexValidator

from conventions.models.convention import Convention
from instructeurs.models import Administration


class UpdateConventionAdministrationForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_authenticated:
            self.fields["administration"].queryset = user.administrations()

    administration = forms.ModelChoiceField(
        label="Administration",
        queryset=Administration.objects.none(),
        to_field_name="uuid",
        error_messages={
            "required": "Vous devez choisir une administration",
            "min_length": "min : Vous devez choisir une administration",
            "invalid_choice": "invalid : Vous devez choisir une administration",
        },
    )

    verification = forms.CharField(
        label="Vérification",
        validators=[RegexValidator("transférer")],
        required=True,
        error_messages={
            "required": "Vous devez recopier le mot pour valider l'opération",
        },
    )

    convention = forms.CharField(widget=forms.HiddenInput())

    def submit(self, request):
        convention = Convention.objects.get(pk=self.cleaned_data["convention"])
        new_administration = self.cleaned_data["administration"]
        convention.programme.administration = new_administration
        convention.programme.save()
