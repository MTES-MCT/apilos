from django import forms
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
            "min_length": "min : Vous devez choisir un bailleur",
            "invalid_choice": "invalid : Vous devez choisir un bailleur",
        },
    )


class ConventionBailleurForm(forms.Form):
    uuid = forms.UUIDField(required=False)

    signataire_nom = forms.CharField(
        label="Nom du signataire de la convention",
        max_length=255,
        error_messages={
            "required": "Le nom du signataire de la convention est obligatoire",
            "max_length": "Le nom du signataire de la convention "
            + "ne doit pas excéder 255 caractères",
        },
        required=False,
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

    identification_bailleur = forms.BooleanField(
        required=False,
        label="Personaliser l'identification du bailleur qui apparait sur la première page de la convention",
    )

    identification_bailleur_detail = forms.CharField(
        label="Identification du bailleur personnalisée",
        help_text='Apparaît uniquement sur la première page de la convention, en dessous de "d\'une part". '
        'Doit contenir la mention "représenté par".',
        required=False,
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
            "Sur les documents de convention, vous avez la possibilité d'affiner"
            + " l'identité du signataire&nbsp;<strong>à la suite</strong> de la mention"
            + " obligatoire : «&nbsp;Le gestionnaire,&nbsp;»"
        ),
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Bloc signature du gestionnaire ne doit pas excéder 5000 caractères",
        },
    )
    gestionnaire_bloc_info_complementaire = forms.CharField(
        label="Éléments complémentaires concernant le gestionnaire sur la convention",
        help_text=mark_safe(
            "Sur les documents de convention, vous avez la possibilité de préciser"
            + " les informations du gestionnaire (SIRET, SIREN, adresse etc...) "
            + "<strong>avant</strong> la mention «&nbsp;dénommé ci-après le gestionnaire&nbsp;»"
        ),
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le bloc ne doit pas excéder 5000 caractères",
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

        if not self.cleaned_data.get("identification_bailleur"):
            if not self.cleaned_data.get("signataire_nom"):
                self.add_error(
                    "signataire_nom",
                    "Le nom du signataire de la convention est obligatoire",
                )
        else:
            if not self.cleaned_data.get("identification_bailleur_detail"):
                self.add_error(
                    "identification_bailleur_detail",
                    "Le détail de l'identification du bailleur est obligatoire "
                    "lorsque vous avez choisi l'identification du bailleur personnalisée",
                )
