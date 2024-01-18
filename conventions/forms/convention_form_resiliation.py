from django import forms


class ConventionResiliationForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
        label="Résiliation",
    )
    date_resiliation = forms.DateField(
        required=True,
        label="Spécifier la date de résiliation",
        error_messages={
            "required": "Vous devez saisir une date de résiliation",
        },
    )
    motif_resiliation = forms.CharField(
        required=True,
        label="Indiquez ici le motif de la résiliation de la convention.",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    champ_libre_avenant = forms.CharField(
        required=False,
        label="Ajoutez tous les renseignements supplémentaires concernant la résiliation.",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
