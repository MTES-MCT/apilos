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
    pieces_jointes = forms.CharField(required=False, label="Fichier joint")
    pieces_jointes_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type docx sont acceptés dans la limite de 100 Mo",
    )
