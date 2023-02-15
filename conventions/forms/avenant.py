from django import forms

from conventions.models import AvenantType


class AvenantForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
    )

    avenant_type = forms.ChoiceField(
        label="Type d'avenant",
        choices=AvenantType.get_as_choices,
        required=True,
    )


class InitavenantsforavenantForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
    )


class AvenantsforavenantForm(forms.Form):

    avenant_types = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label="Type d'avenant",
        choices=AvenantType.get_as_choices,
        required=True,
    )
    error_messages = (
        {
            "required": "Vous devez saisir un ou plusieurs types d'avenant",
        },
    )
    desc_avenant = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Informations sur la nature de l'avenant.",
    )
    nom_fichier_signe = forms.FileField(
        required=False,
    )


class CompleteforavenantForm(forms.Form):
    """
    Formulaire qui permet à l'instructeur de compléter les informations de la convention 
      non-connue d'Apilos avant la validation de l'avenant
    """

    ville = forms.CharField(
        label="Ville",
        max_length=255,
        required=False,
        error_messages={
            "max_length": "La ville ne doit pas excéder 255 caractères",
        },
    )    
    nb_logements = forms.IntegerField(
        label="Nb logements à conventionner",
        required=False,
    )
    nom_fichier_signe = forms.FileField(
        required=False,
    )
