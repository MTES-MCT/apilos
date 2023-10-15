"""
Étape Commentaires du formulaire par étape de la convention
"""

from django import forms

from files.forms import MultipleFileField


class ConventionCommentForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
        label="Commentaires",
    )

    attached = forms.CharField(
        required=False,
        label="Fichiers à joindre à la convention",
        help_text="Déposez ici les fichiers à joindre à votre convention le cas"
        + " echéant et si nécessaire, par exemple"
        + " \r\n  • Autorisation délivrée au gestionnaire par le président du conseil"
        + " départemental ou par l'autorité compétente de l'état dans le cadre d'un"
        + " foyer hors habitat inclusif"
        + " \r\n  • Convention de location"
        + " \r\n  • Programme et des travaux"
        + " \r\n  • Échéancier du programme des travaux"
        + " \r\n  • …",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    attached_files = forms.CharField(
        required=False,
    )

    commentaires_text = forms.CharField(
        required=False,
        label="Ajoutez vos commentaires à l'attention de l'instructeur",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )

    commentaires_files = MultipleFileField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )
