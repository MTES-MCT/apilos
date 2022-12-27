from django import forms
from django.core.exceptions import ValidationError


class ConventionNumberForm(forms.Form):
    convention = None
    convention_numero = forms.CharField(
        max_length=250,
        label="Numéro de convention",
        error_messages={
            "max_length": (
                "La longueur totale du numéro de convention ne peut pas excéder"
                + " 250 caractères"
            ),
            "required": "Le numéro de convention est obligatoire",
        },
    )

    def clean_convention_numero(self):
        convention_numero = self.cleaned_data.get("convention_numero", 0)
        if convention_numero == self.convention.get_convention_prefix():
            raise ValidationError(
                "Attention, le champ est uniquement prérempli avec le préfixe du numéro de "
                + "convention déterminé pour votre administration. Il semble que vous n'ayez pas "
                + "ajouté, à la suite de ce préfixe, de numéro d'ordre de la convention."
            )
        return convention_numero
