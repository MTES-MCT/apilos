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
        label="Ajoutez tous les renseignements supplémentaires, de type désignation des immeubles, "
        "origines des propriétés ou autre, que vous souhaitez voir apparaître dans l'avenant'. "
        "Ces informations apparaîtront à la fin de l'avenant.",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
