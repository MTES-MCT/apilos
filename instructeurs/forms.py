from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from instructeurs.models import Administration


class AdministrationForm(forms.Form):
    uuid = forms.UUIDField(required=False)
    nom = forms.CharField(
        label="Nom de l'administration",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le nom de l'administration est obligatoire",
            "min_length": "Le nom de l'administration est obligatoire",
            "max_length": "Le nom de l'administration ne doit pas excéder 255 caractères",
        },
    )

    def clean_nom(self):
        nom = self.cleaned_data["nom"]
        if (
            Administration.objects.filter(nom=nom)
            .exclude(uuid=self.cleaned_data["uuid"])
            .exists()
        ):
            raise ValidationError(
                "Le nom de l'administration existe déjà, il doit-être unique"
            )
        return nom

    code = forms.CharField(
        label="Code de l'administration",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le code de l'administration est obligatoire",
            "min_length": "Le code de l'administration est obligatoire",
            "max_length": "Le code de l'administration ne doit pas excéder 255 caractères",
        },
    )

    def clean_code(self):
        code = self.cleaned_data["code"]
        if (
            Administration.objects.filter(code=code)
            .exclude(uuid=self.cleaned_data["uuid"])
            .exists()
        ):
            raise ValidationError(
                "Le code de l'administration existe déjà, il doit-être unique"
            )
        return code

    ville_signature = forms.CharField(
        required=False,
        label="Ville de signature de la convention",
        max_length=255,
        error_messages={
            "max_length": "La ville de signature ne doit pas excéder 255 caractères",
        },
    )
    prefix_convention = forms.CharField(
        required=False,
        label="Préfixe du numéro de convention",
        max_length=255,
        error_messages={
            "max_length": "Le préfixe du numérp de convention ne doit pas excéder 255 caractères",
        },
          help_text=mark_safe(
            "Pour remplir le préfixe dynamiquement, vous pouvez utiliser les caractères automatiques suivants : <br/>"
            + " <b>{département}</b> : numéro du département <br/>"
            + " <b>{zone}</b> : numéro de la zone <br/>"
            + " <b>{mois} et {année}</b> : mois et année en cours. <br/>"
            + "Vous pouvez également choisir les séparateurs de votre choix entre ces caractères ainsi qu'ajouter le texte qui vous convient."
        ),
    )
