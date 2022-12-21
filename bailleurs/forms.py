from django import forms
from django.core.exceptions import ValidationError

from core import forms_utils

from bailleurs.models import Bailleur, SousNatureBailleur


class UpdateBailleurForm(forms.Form):
    def __init__(self, *args, bailleurs=None, **kwargs) -> None:
        self.declared_fields["bailleur"].choices = bailleurs
        super().__init__(*args, **kwargs)

    bailleur = forms.ChoiceField(
        label="Bailleur",
        choices=[],
        error_messages={
            "required": "Vous devez choisir un bailleur",
        },
    )


class ConventionBailleurForm(forms.Form):
    uuid = forms.UUIDField(required=False)

    nom = forms.CharField(
        required=True,
        label="Nom du bailleur",
        error_messages={
            "required": "Le nom du bailleur est obligatoire",
            "max_length": "Le nom du bailleur ne doit pas excéder 255 caractères",
        },
    )
    siret = forms.CharField(
        label="SIRET",
        max_length=14,
        min_length=14,
        error_messages={
            "required": "Le SIRET du bailleur est obligatoire",
            "max_length": "Le SIRET doit comporter 14 caractères",
            "min_length": "Le SIRET doit comporter 14 caractères",
        },
    )

    def clean_siret(self):
        siret = self.cleaned_data["siret"]
        if (
            Bailleur.objects.filter(siret=siret)
            .exclude(uuid=self.cleaned_data["uuid"])
            .exists()
        ):
            raise ValidationError(
                "Le siret du bailleur existe déjà, il doit-être unique"
            )
        return siret

    capital_social = forms.FloatField(
        required=False,
        label="Capital social",
    )
    (adresse, code_postal, ville) = forms_utils.address_form_fields()
    signataire_nom = forms.CharField(
        label="Nom du signataire de la convention",
        max_length=255,
        error_messages={
            "required": "Le nom du signataire de la convention est obligatoire",
            "max_length": "Le nom du signataire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
    )
    signataire_fonction = forms.CharField(
        label="Fonction du signataire de la convention",
        max_length=255,
        error_messages={
            "required": "La fonction du signataire de la convention est obligatoire",
            "max_length": "La fonction du signataire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
    )
    signataire_date_deliberation = forms.DateField(
        label="Date de délibération",
        error_messages={
            "required": "La date de délibération est obligatoire",
        },
        help_text=(
            "Date à laquelle le signataire a reçu le mandat lui "
            + "permettant de signer la convention"
        ),
    )

    sous_nature_bailleur = forms.TypedChoiceField(
        required=False, label="Type de bailleur", choices=SousNatureBailleur.choices
    )

    gestionnaire = forms.CharField(
        label="Entreprise gestionnaire",
        required=False,
        max_length=255,
        error_messages={
            "max_length": "L'entreprise gestionnaire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
    )

    gestionnaire_signataire_nom = forms.CharField(
        label="Nom du signataire du gestionnaire de la convention",
        required=False,
        max_length=255,
        error_messages={
            "max_length": "Le nom du signataire du gestionnaire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
    )
    gestionnaire_signataire_fonction = forms.CharField(
        label="Fonction du signataire du gestionnaire de la convention",
        required=False,
        max_length=255,
        error_messages={
            "max_length": "La fonction du signataire du gestionnaire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
    )
    gestionnaire_signataire_date_deliberation = forms.DateField(
        label="Date de délibération",
        required=False,
        help_text=(
            "Date à laquelle le signataire du gestionnaire a reçu le mandat lui "
            + "permettant de signer la convention"
        ),
    )

    def clean(self):
        gestionnaire = self.cleaned_data.get("gestionnaire", None)
        gestionnaire_signataire_nom = self.cleaned_data.get(
            "gestionnaire_signataire_nom", None
        )
        gestionnaire_signataire_fonction = self.cleaned_data.get(
            "gestionnaire_signataire_fonction", None
        )
        gestionnaire_signataire_date_deliberation = self.cleaned_data.get(
            "gestionnaire_signataire_date_deliberation", None
        )
        if gestionnaire:
            if not gestionnaire_signataire_nom:
                self.add_error(
                    "gestionnaire_signataire_nom",
                    "Lorsque l'entreprise gestionnaire est renseignée, Le nom du"
                    + " signataire du gestionnaire de la convention doit être"
                    + " renseigné",
                )
            if not gestionnaire_signataire_fonction:
                self.add_error(
                    "gestionnaire_signataire_fonction",
                    "Lorsque l'entreprise gestionnaire est renseignée, La fonction du"
                    + " signataire du gestionnaire de la convention doit être"
                    + " renseignée",
                )
            if not gestionnaire_signataire_date_deliberation:
                self.add_error(
                    "gestionnaire_signataire_date_deliberation",
                    "Lorsque l'entreprise gestionnaire est renseignée, La date de"
                    + " délibération du signataire du gestionnaire de la convention"
                    + " doit être renseignée",
                )


class BailleurForm(ConventionBailleurForm):
    def __init__(self, *args, bailleurs=None, **kwargs) -> None:
        if bailleurs:
            self.declared_fields["bailleur"].choices = bailleurs
        super().__init__(*args, **kwargs)

    bailleur = forms.ChoiceField(
        required=False,
        label="Bailleur parent",
        help_text="Les utilisateurs du bailleur parent à les mêmes droits sur ce bailleur",
        initial=None,
        choices=[],
    )
