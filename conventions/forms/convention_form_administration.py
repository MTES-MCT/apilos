from django import forms
from django.core.validators import RegexValidator

from instructeurs.models import Administration


class UpdateConventionAdministrationForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        validators=[RegexValidator("TRANSFÉRER")],
        required=True,
        error_messages={
            "required": "Vous devez recopier le mot pour valider l'opération",
        },
    )

    def submit(self, request):
        pass
