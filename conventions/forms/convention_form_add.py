from django import forms
from django.db.models import QuerySet

from bailleurs.models import Bailleur
from programmes.models.choices import ActiveNatureLogement, FinancementEDD


class ConventionAddForm(forms.Form):
    def __init__(
        self, *args, bailleur_query: QuerySet, administrations=None, **kwargs
    ) -> None:
        self.declared_fields["administration"].choices = administrations
        self.declared_fields["bailleur"].queryset = bailleur_query

        super().__init__(*args, **kwargs)

    numero = forms.CharField(
        label="Numéro de la convention",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le numéro de la convention est obligatoire",
            "min_length": "Le numéro de la convention est obligatoire",
            "max_length": "Le numéro de la convention ne doit pas excéder 255 caractères",
        },
    )
    nom = forms.CharField(
        label="Nom de la convention",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le nom de la convention est obligatoire",
            "min_length": "Le nom de la convention est obligatoire",
            "max_length": "Le nom de la convention ne doit pas excéder 255 caractères",
        },
    )
    bailleur = forms.ModelChoiceField(
        label="Bailleur",
        queryset=Bailleur.objects.none(),
        help_text="Recherchez par nom ou SIREN",
        to_field_name="uuid",
        error_messages={
            "required": "Le bailleur est obligatoire",
        },
    )
    administration = forms.ChoiceField(
        label="Administration",
        choices=[],
        help_text="Délégataire des aides à la pierre du territoire de l'opération",
        error_messages={
            "required": "L'administration est obligatoire",
        },
    )
    nature_logement = forms.ChoiceField(
        label="Nature des logements",
        choices=ActiveNatureLogement.choices,
        error_messages={
            "required": "La selection de la nature des logements est obligatoire"
        },
    )
    nb_logements = forms.IntegerField(
        label="Nombre de logements conventionnés",
        error_messages={
            "required": "Le nombre de logements conventionnés est obligatoire",
        },
    )
    financement = forms.TypedChoiceField(
        label="Type de financement",
        choices=FinancementEDD.choices,
        error_messages={
            "required": "Le financement est obligatoire",
        },
    )
    annee_signature = forms.DateField(
        label="Année de signature de la convention",
    )
