"""
Étape Commentaires du formulaire par étape de la convention
"""

from django import forms


class ConventionChampLibreForm(forms.Form):

    uuid = forms.UUIDField(
        required=False,
        label="Champ Libre",
    )
    champ_libre_avenant = forms.CharField(
        required=False,
        label="Ajoutez vos informations complémentaires",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
