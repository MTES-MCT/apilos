from django import forms

from conventions.models import TypeEvenement


class EvenementForm(forms.Form):
    uuid = forms.UUIDField(required=False)
    description = forms.CharField(
        label="Détail de l'évènement",
    )
    type_evenement = forms.TypedChoiceField(
        required=True,
        label="Type d'évènement",
        choices=TypeEvenement.choices,
    )
