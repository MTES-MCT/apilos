from django import forms
from django.core.exceptions import ValidationError

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
