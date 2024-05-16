"""
Étape Financement du formulaire par étape de la convention
"""

import datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from conventions.models import Preteur
from programmes.models import Financement, TypeOperation


class ConventionFinancementForm(forms.Form):
    """
    Formulaire définissant les informations de financement de la convention
    """

    # ces attributs sont initialisés avant la validation du formulaire
    # ils sont utilisés pour valider la date de fin de conventionnement
    prets = []
    convention = None

    uuid = forms.UUIDField(
        required=False,
        label="Prêts et financements",
    )
    annee_fin_conventionnement = forms.IntegerField(
        required=True,
        label="",
        initial=datetime.date.today().year,
        max_value=datetime.date.today().year + 500,
        min_value=1977,
        error_messages={
            "required": "La date de fin de conventionnement est obligatoire",
            "max_value": "La fin de conventionnement ne peut être dans plus de 500 ans",
            "min_value": "La fin de conventionnement ne peut être antérieur à 1977",
        },
    )
    fond_propre = forms.FloatField(
        required=False,
        label="Fonds propres",
    )
    historique_financement_public = forms.CharField(
        required=False,
        label="Historique de financement public",
        max_length=5000,
        error_messages={
            "max_length": "L'historique de financement public ne doit pas excéder 5000 caractères",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        annee_fin_conventionnement = cleaned_data.get("annee_fin_conventionnement")

        if (
            self.prets
            and self.convention is not None
            and annee_fin_conventionnement is not None
        ):
            if self.convention.is_outre_mer:
                self._outre_mer_end_date_validation(annee_fin_conventionnement)
            elif self.convention.financement == Financement.PLS:
                self._pls_end_date_validation(annee_fin_conventionnement)
            elif self.convention.programme.type_operation == TypeOperation.SANSTRAVAUX:
                self._sans_travaux_end_date_validation(annee_fin_conventionnement)
            else:
                self._other_end_date_validation(annee_fin_conventionnement)

    def _outre_mer_end_date_validation(self, annee_fin_conventionnement):
        today = datetime.date.today()
        if self.convention.parent:
            if self.convention.parent.televersement_convention_signee_le:
                today = self.convention.parent.televersement_convention_signee_le

        # La durée du conventionnement ne peut pas être inférieure à 9 ans
        min_years = today.year + 9
        if annee_fin_conventionnement < min_years:
            self.add_error(
                "annee_fin_conventionnement",
                (
                    "L'année de fin de conventionnement ne peut être inférieure à "
                    + f"{min_years}"
                ),
            )

        # Si financement, le conventionnement doit couvrir la durée des prêts
        if self.convention.programme.type_operation == TypeOperation.SANSTRAVAUX:
            return

        for pret in self.prets:
            if pret.cleaned_data["date_octroi"] and pret.cleaned_data["duree"]:
                end_datetime = pret.cleaned_data["date_octroi"] + relativedelta(
                    years=int(pret.cleaned_data["duree"])
                )
                if annee_fin_conventionnement < end_datetime.year:
                    self.add_error(
                        "annee_fin_conventionnement",
                        (
                            "L'année de fin de conventionnement ne peut être inférieure à "
                            + f"{end_datetime}"
                        ),
                    )

    def _pls_end_date_validation(self, annee_fin_conventionnement):
        """
        Validation : date de fin de conventionnement pour un PLS
          entre 15 et 40 ans après la date de début de conventionnement (date courante)
          et finissant au 30 juin
        """
        today = datetime.date.today()
        if self.convention.parent:
            if self.convention.parent.televersement_convention_signee_le:
                today = self.convention.parent.televersement_convention_signee_le
        min_years = today.year + 15
        max_years = today.year + 40
        if today.month > 6:
            min_years = min_years + 1
            max_years = max_years + 1
        if annee_fin_conventionnement < min_years:
            self.add_error(
                "annee_fin_conventionnement",
                (
                    "L'année de fin de conventionnement ne peut être inférieur à "
                    + f"{min_years}"
                ),
            )
        # No control on max date for foyer, residence and avenants
        if (
            self.convention.programme.is_foyer()
            or self.convention.programme.is_residence()
            or self.convention.is_avenant()
        ):
            return
        if annee_fin_conventionnement > max_years:
            self.add_error(
                "annee_fin_conventionnement",
                (
                    "L'année de fin de conventionnement ne peut être supérieur à "
                    + f"{max_years}"
                ),
            )

    def _sans_travaux_end_date_validation(self, annee_fin_conventionnement):
        """
        Validation: date de fin de conventionnement pour un programme sans travaux
          minimum 9 ans après la date de début de conventionnement (date courante)
          et finissant au 30 juin
        """
        today = datetime.date.today()
        if self.convention.parent:
            if self.convention.parent.televersement_convention_signee_le:
                today = self.convention.parent.televersement_convention_signee_le

        min_years = today.year + 9
        if today.month > 6:
            min_years = min_years + 1
        if annee_fin_conventionnement < min_years:
            self.add_error(
                "annee_fin_conventionnement",
                (
                    "L'année de fin de conventionnement ne peut être inférieur à "
                    + f"{min_years}"
                ),
            )

    def _other_end_date_validation(self, annee_fin_conventionnement):
        """
        Validation: date de fin de conventionnement pour un programme avec travaux
          minimum 9 ans après la date de début de conventionnement (date courante)
          minimum après la fin du dernier prêt CDC
          pour les convention de type HLM, SEM, type 1 & 2 : finissant au 30 juin
          pour les convention de type Foyer & Résidence : finissant au 31 décembre
        """
        end_conv = None
        cdc_pret = None
        for pret in self.prets:
            if pret.cleaned_data["preteur"] in ["CDCF", "CDCL"]:
                if pret.cleaned_data["date_octroi"] and pret.cleaned_data["duree"]:
                    end_datetime = pret.cleaned_data["date_octroi"] + relativedelta(
                        years=int(pret.cleaned_data["duree"])
                    )
                    if not end_conv or end_datetime > end_conv:
                        end_conv = end_datetime
                        cdc_pret = pret
        if end_conv and cdc_pret:
            cdc_end_year = end_conv.year
            if end_conv.year - cdc_pret.cleaned_data["date_octroi"].year < 9:
                cdc_end_year = cdc_pret.cleaned_data["date_octroi"].year + 9
            # don't add a year for FOYER because end of convention is the 31/12
            if (
                not self.convention.programme.is_foyer()
                and not self.convention.programme.is_residence()
                and end_conv
                and end_conv.month > 6
            ):
                cdc_end_year = cdc_end_year + 1
            if annee_fin_conventionnement < cdc_end_year:
                self.add_error(
                    "annee_fin_conventionnement",
                    (
                        "L'année de fin de conventionnement ne peut être inférieur à "
                        + f"{cdc_end_year}"
                    ),
                )


class PretForm(forms.Form):
    """
    Formulaire pour un prêt : une ligne dans le tableau des prêts
    """

    uuid = forms.UUIDField(
        required=False,
        label="Prêt ou financement",
    )
    numero = forms.CharField(
        required=False,
        label="",
        max_length=255,
        error_messages={
            "max_length": "Le numero ne doit pas excéder 255 caractères",
        },
    )
    preteur = forms.TypedChoiceField(required=False, label="", choices=Preteur.choices)
    autre = forms.CharField(
        required=False,
        label="",
        max_length=255,
        error_messages={
            "max_length": "Le prêteur ne doit pas excéder 255 caractères",
        },
    )
    date_octroi = forms.DateField(
        required=False,
        label="",
    )
    duree = forms.IntegerField(
        required=False,
        label="",
    )
    montant = forms.DecimalField(
        label="",
        max_digits=12,
        decimal_places=2,
        error_messages={
            "required": "Le montant du prêt est obligatoire",
            "max_digits": "Le montant du prêt doit-être inférieur à 10 000 000 000 €",
        },
    )

    def clean(self):
        """
        Validations:
          - si le prêteur est CDCF ou CDCL, numéro,date d'octroi et durée sont obligatoires
          - si le prêteur est autre, le champ autre est obligatoire
        """
        cleaned_data = super().clean()
        preteur = cleaned_data.get("preteur")

        if preteur in ["CDCF", "CDCL"]:
            if not cleaned_data.get("date_octroi"):
                self.add_error(
                    "date_octroi",
                    "La date d'octroi est obligatoire pour un prêt de la "
                    + "Caisse de dépôts et consignations",
                )
            if not cleaned_data.get("duree"):
                self.add_error(
                    "duree",
                    "La durée est obligatoire pour un prêt de la Caisse de dépôts et consignations",
                )
            if not cleaned_data.get("numero"):
                self.add_error(
                    "numero",
                    (
                        "Le numéro est obligatoire pour un prêt"
                        + " de la Caisse de dépôts et consignations"
                    ),
                )
        if preteur in ["AUTRE"]:
            if not cleaned_data.get("autre"):
                self.add_error("autre", "Merci de préciser le prêteur")


class BasePretFormSet(BaseFormSet):
    """
    Liste de formulaire Pret : tableau des prêts
    """

    # attrubut assigné avant la validation
    convention = None

    def clean(self):
        self.manage_cdc_validation()

    def validate_initial_numero_unicity(self) -> bool:
        is_valid = True
        numeros = [form.initial.get("numero") for form in self.forms]
        for form in self.forms:
            num = form.initial.get("numero")
            if numeros.count(num) > 1:
                form.errors["numero"] = [
                    f"Le numéro de financement {num} n'est pas unique."
                ]
                is_valid = False
        return is_valid

    def manage_cdc_validation(self):
        """
        Validation : Hors convention PLS et Sans Travaux,
        au moins un prêt CDCF ou CDCL doit-être déclaré
        """
        if (
            self.convention is not None
            and self.convention.financement != Financement.PLS
            and self.convention.programme.type_operation != TypeOperation.SANSTRAVAUX
        ):
            for form in self.forms:
                if form.cleaned_data.get("preteur") in ["CDCF", "CDCL"]:
                    return
            error = ValidationError(
                "Au moins un prêt à la Caisee des dépôts et consignations doit-être déclaré "
                + "(CDC foncière, CDC locative)"
            )
            self._non_form_errors.append(error)


PretFormSet = formset_factory(PretForm, formset=BasePretFormSet, extra=0)
