import re
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
    signataire_bloc_signature = forms.CharField(
        required=False,
        label="Élément additionnel de signature sur la convention",
        max_length=5000,
        help_text=mark_safe(
            "Sur les documents de convention, vous avez la possibilité d'affiner l'identité"
            + " du signataire&nbsp;<strong>à la suite</strong> de la mention obligatoire :&nbsp;"
            + "«&nbsp;Le préfet, le président de l'établissement public de coopération"
            + "intercommunale, du conseil départemental, de la métropole…&nbsp;»"
        ),
    )

    def clean_signataire_bloc_signature(self):
        signataire_bloc_signature = self.cleaned_data.get(
            "signataire_bloc_signature", 0
        )

        # Automatically add a trailing comma so signature label remains compliant
        signataire_bloc_signature = signataire_bloc_signature.strip(" ,") + ","

        return signataire_bloc_signature

    prefix_convention = forms.CharField(
        required=False,
        label="Préfixe du numéro de convention",
        max_length=255,
        error_messages={
            "max_length": "Le préfixe du numéro de convention ne doit pas excéder 255 caractères",
        },
        help_text=mark_safe(
            "Pour remplir le préfixe dynamiquement, vous pouvez utiliser les caractères "
            + "automatiques suivants : <br/>"
            + " <strong>{département}</strong> : numéro du département <br/>"
            + " <strong>{zone}</strong> : numéro de la zone <br/>"
            + " <strong>{mois} et {année}</strong> : mois et année en cours. <br/>"
            + "Vous pouvez également choisir les séparateurs de votre choix entre ces caractères "
            + "ainsi qu'ajouter le texte qui vous convient."
        ),
    )

    def clean_prefix_convention(self):
        prefix_convention = self.cleaned_data.get("prefix_convention", 0)

        test_prefix = re.findall(r"\{\w+\}", prefix_convention)
        for element in test_prefix:
            if element not in ["{département}", "{zone}", "{mois}", "{année}"]:
                raise ValidationError(
                    f"Vous ne pouvez pas utiliser {element} comme élement dynamique."
                    + "Seuls {département}, {zone}, {mois} et {année} sont autorisés"
                )
        return prefix_convention

    adresse = forms.CharField(
        required=False,
        label="Adresse de l'administration",
        max_length=5000,
        error_messages={
            "max_length": "L'adresse ne doit pas excéder 5000 caractères",
        },
    )
    code_postal = forms.CharField(
        required=False,
        label="Code postal",
        max_length=255,
        error_messages={
            "max_length": "Le code postal ne doit pas excéder 255 caractères",
        },
    )
    ville = forms.CharField(
        required=False,
        label="Ville",
        max_length=255,
        error_messages={
            "max_length": "La ville ne doit pas excéder 255 caractères",
        },
    )

    nb_convention_exemplaires = forms.IntegerField(
        required=True,
        label=(
            "Nombre d'exemplaire de la convention que le bailleur doit envoyer au service"
            + " instructeur"
        ),
        help_text="Ce nombre d'exemplaire est utilisé pour customiser l'email envoyé au"
        + " bailleur lorsque la convention est validée.",
    )
