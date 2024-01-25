from django import forms

error_message_max_length = "Le message ne doit pas excéder 5000 caractères"


class ConventionResiliationActeForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
        label="Résiliation",
    )
    fichier_instruction_resiliation = forms.CharField(
        required=False,
        label="Acte administratif (arrêté)",
        max_length=5000,
        error_messages={
            "max_length": error_message_max_length,
        },
    )
    fichier_instruction_resiliation_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )


class ConventionResiliationForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
        label="Résiliation",
    )
    date_resiliation = forms.DateField(
        required=True,
        label="Indiquez la date de résiliation",
        error_messages={
            "required": "Vous devez saisir une date de résiliation",
        },
    )
    motif_resiliation = forms.CharField(
        required=True,
        label="Indiquez ici le motif de la résiliation de la convention.",
        max_length=5000,
        error_messages={
            "max_length": error_message_max_length,
        },
    )
    commentaires = forms.CharField(
        required=False,
        label="Ajoutez vos commentaires à l'attention de l'instructeur",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    commentaires_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )
