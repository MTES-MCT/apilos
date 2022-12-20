from django import forms
from django.forms import formset_factory


class LotCollectifForm(forms.Form):
    uuid = forms.UUIDField()
    foyer_residence_nb_garage_parking = forms.IntegerField(
        required=False,
        label="Garages et/ ou parking (nombre)",
    )
    foyer_residence_dependance = forms.CharField(
        required=False,
        label="Dépendances (nombre et surface)",
        max_length=5000,
        error_messages={
            "max_length": "la description des dépendances ne doit pas excéder 5000 caractères",
        },
    )
    foyer_residence_locaux_hors_convention = forms.CharField(
        required=False,
        label="Locaux auxquels ne s'appliquent pas la convention (Liste)",
        help_text="Exemple : logement de fonction, logement d'accueil temporaire et"
        + " espaces hors hébergement dédiés aux soins, à de la balnéothérapie ...",
        max_length=5000,
        error_messages={
            "max_length": "la description des dépendances ne doit pas excéder 5000 caractères",
        },
    )


class LocauxCollectifsForm(forms.Form):
    uuid = forms.UUIDField(required=False)
    type_local = forms.CharField(
        label="",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le type de locaux est obligatoire",
            "min_length": "Le type de locaux est obligatoire",
            "max_length": "L'adresse ne doit pas excéder 255 caractères",
        },
    )
    surface_habitable = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "max_digits": "La surface habitable du local collectif doit-être inférieur à 10000 m²",
            "required": "La surface habitable est obligatoire",
        },
    )
    nombre = forms.IntegerField(
        label="",
        error_messages={
            "required": "Le nombre de locaux est obligatoire",
        },
    )


LocauxCollectifsFormSet = formset_factory(
    LocauxCollectifsForm, formset=forms.BaseFormSet, extra=0
)
