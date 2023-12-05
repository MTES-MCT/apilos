"""
Étape Commentaires du formulaire par étape de la convention
"""

from django import forms


class ConventionDenonciationForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
        label="Dénonciation",
    )
    date_denonciation = forms.DateField(
        required=True,
        label="Indiquez la date de dénonciation.",
        help_text="""
           La dénonciation intervient à date d'échéance de la convention, c'est à dire sa date de fin ou de renouvellement (tous les 3 ans).
           La notification de dénonciation doit être faite au moins 6 mois avant l'échéance de la convention par acte authentique (acte notarié ou acte d'huissier de justice).
           Si ces conditions ne sont pas respectées, elle ne pourra être validée par l'administration instructrice.
        """,  # noqa: E501
        error_messages={
            "required": "Vous devez saisir une date de dénonciation",
        },
    )
    motif_denonciation = forms.CharField(
        required=False,
        label="Indiquez ici le motif de la dénonciation de la convention.",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    fichier_instruction_denonciation = forms.CharField(
        required=False, label="Acte authentique/administratif"
    )
    fichier_instruction_denonciation_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )
