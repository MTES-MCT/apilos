"""
Étape Annexes du formulaire par étape de la convention (type HLM, SEM, Type I & 2)
"""

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from core.utils import round_half_up
from programmes.models import (
    Logement,
    TypologieAnnexe,
    TypologieLogementClassique,
)


class LotAnnexeForm(forms.Form):
    """
    Formulaire pour les types d'annexes d'une convention (tag ou case à cocher)
    """

    uuid = forms.UUIDField(required=False)
    annexe_caves = forms.BooleanField(
        required=False,
        label="Caves",
    )
    annexe_soussols = forms.BooleanField(
        required=False,
        label="Sous-sols",
    )
    annexe_remises = forms.BooleanField(
        required=False,
        label="Remises",
    )
    annexe_ateliers = forms.BooleanField(
        required=False,
        label="Ateliers",
    )
    annexe_sechoirs = forms.BooleanField(
        required=False,
        label="Séchoirs",
    )
    annexe_celliers = forms.BooleanField(
        required=False,
        label="Celliers extérieurs au logement",
    )
    annexe_resserres = forms.BooleanField(required=False, label="Resserres")
    annexe_combles = forms.BooleanField(
        required=False,
        label="Combles et greniers aménageables",
    )
    annexe_balcons = forms.BooleanField(
        required=False,
        label="Balcons",
    )
    annexe_loggias = forms.BooleanField(
        required=False,
        label="Loggias et Vérandas",
    )
    annexe_terrasses = forms.BooleanField(
        required=False,
        label="Terrasses",
        help_text=(
            "Dans la limite de 9 m2, les parties de terrasses accessibles en étage ou aménagées"
            + " sur ouvrage enterré ou à moitié enterré"
        ),
    )


class AnnexeForm(forms.Form):
    """
    Formulaire Annexe formant la liste des annexes d'une convention : une ligne du
      tableau des annexes
    """

    uuid = forms.UUIDField(
        required=False,
        label="Annexe",
    )
    typologie = forms.TypedChoiceField(
        required=True,
        label="",
        choices=TypologieAnnexe.choices,
    )
    logement_designation = forms.CharField(
        label="",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "La designation du logement est obligatoire",
            "min_length": "La designation du logement est obligatoire",
            "max_length": "La designation du logement ne doit pas excéder 255 caractères",
        },
    )
    logement_typologie = forms.TypedChoiceField(
        required=True, label="", choices=TypologieLogementClassique.choices
    )
    surface_hors_surface_retenue = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface habitable est obligatoire",
            "max_digits": "La surface habitable doit-être inférieur à 10000 m²",
        },
    )
    loyer_par_metre_carre = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer par m² est obligatoire",
            "max_digits": "La loyer par m² doit-être inférieur à 10000 €",
        },
    )
    loyer = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer est obligatoire",
            "max_digits": "La loyer doit-être inférieur à 10000 €",
        },
    )

    def clean_loyer(self):
        """
        Validation du loyer :
            - le loyer ne peut être supérieur au produit de la surface de l'annexe
              et du loyer par mètre carré (tolérance de 0,1 €)
        """
        surface_hors_surface_retenue = self.cleaned_data.get(
            "surface_hors_surface_retenue", 0
        )
        loyer_par_metre_carre = self.cleaned_data.get("loyer_par_metre_carre", 0)
        loyer = self.cleaned_data.get("loyer", 0)

        # check that lot_id exist in DB
        if round_half_up(loyer, 2) > (
            round_half_up(surface_hors_surface_retenue * loyer_par_metre_carre, 2) + 0.1
        ):
            raise ValidationError(
                "Le loyer ne peut être supérieur au produit de la surface"
                + " de l'annexe et du loyer par mètre carré. valeur attendue :"
                + f" {round_half_up(surface_hors_surface_retenue*loyer_par_metre_carre,2)} €"
                + " (tolérance de 0,1 €)"
            )

        return loyer


class BaseAnnexeFormSet(BaseFormSet):
    """
    Liste de formulaire Annexe : tableau des annexes
    """

    convention = None

    def clean(self):
        self.manage_logement_exists_validation()

    def manage_logement_exists_validation(self):
        """
        Validation du formulaire :
            - le logement doit exister dans le lot
        """
        if not self.convention:
            return

        for form in self.forms:
            if (
                Logement.objects.filter(
                    lot__in=self.convention.lots.values("id")
                ).count()
                == 0
            ):
                form.add_error(
                    "logement_designation", "Ce logement n'existe pas dans ce lot"
                )


AnnexeFormSet = formset_factory(AnnexeForm, formset=BaseAnnexeFormSet, extra=0)
