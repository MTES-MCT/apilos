from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils.safestring import mark_safe

from bailleurs.models import Bailleur, NatureBailleur, SousNatureBailleur


class ChangeBailleurForm(forms.Form):
    def __init__(self, *args, bailleur_query: QuerySet, **kwargs) -> None:
        self.declared_fields["bailleur"].queryset = bailleur_query

        super().__init__(*args, **kwargs)

    bailleur = forms.ModelChoiceField(
        label="Bailleur",
        queryset=Bailleur.objects.none(),
        to_field_name="uuid",
        error_messages={
            "required": "Vous devez choisir un bailleur",
        },
    )


class ConventionBailleurForm(forms.Form):
    uuid = forms.UUIDField(required=False)

    nom = forms.CharField(
        required=True,
        label="Nom du bailleur",
        help_text="Tel qu'il sera affiché dans la convention",
        error_messages={
            "required": "Le nom du bailleur est obligatoire",
            "max_length": "Le nom du bailleur ne doit pas excéder 255 caractères",
        },
    )
    siret = forms.CharField(
        label="SIRET",
        min_length=7,
        max_length=14,
        error_messages={
            "required": "Le SIRET du bailleur est obligatoire",
            "max_length": "Le SIRET doit comporter 14 caractères",
            "min_length": "Le SIRET doit comporter 14 caractères",
        },
    )
    siren = forms.CharField(
        label="SIREN",
        required=False,
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

    adresse = forms.CharField(
        label="Adresse",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "L'adresse est obligatoire",
            "min_length": "L'adresse est obligatoire",
            "max_length": "L'adresse ne doit pas excéder 255 caractères",
        },
    )

    code_postal = forms.CharField(
        label="Code postal",
        min_length=5,
        max_length=5,
        error_messages={
            "required": "Le code postal est obligatoire",
            "max_length": "Le code postal est une suite de 5 caractères",
            "min_length": "Le code postal est une suite de 5 caractères",
        },
    )
    ville = forms.CharField(
        label="Ville",
        max_length=255,
        error_messages={
            "required": "La ville est obligatoire",
            "max_length": "La ville ne doit pas excéder 255 caractères",
        },
    )

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
        required=False,
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
        required=False,
    )
    signataire_bloc_signature = forms.CharField(
        required=False,
        label="Élément additionnel de signature du bailleur sur la convention",
        max_length=5000,
        help_text=mark_safe(
            "Sur les documents de convention, vous avez la possibilité d'affiner l'identité"
            + " du signataire&nbsp;<strong>à la suite</strong> de la mention obligatoire : "
            + "«&nbsp;Le bailleur&nbsp;», ou «&nbsp;Le propriétaire&nbsp;»."
        ),
        error_messages={
            "max_length": "Le bloc signature ne doit pas excéder 5000 caractères",
        },
    )

    nature_bailleur = forms.TypedChoiceField(
        required=False, label="Nature du bailleur", choices=NatureBailleur.choices
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
    gestionnaire_signataire_bloc_signature = forms.CharField(
        label="Élément additionnel de signature du gestionnaire sur la convention",
        help_text=mark_safe(
            "Sur les documents de convention, vous avez la possibilité d'affiner l'identité du signataire&nbsp;"
            + "<strong>à la suite</strong> de la mention obligatoire : «&nbsp;Le gestionnaire,&nbsp;»"
        ),
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Bloc signature du gestionnaire ne doit pas excéder 5000 caractères",
        },
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
