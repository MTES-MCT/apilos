"""
Étape Logements du formulaire par étape de la convention,les formulaires ont différents
selon le type de convention :
    - Type HLM, SEM, Type I & 2
    - Foyer Résidence
"""

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from core.utils import round_half_up
from programmes.models import (
    LogementEDD,
    Lot,
    TypologieLogementClassique,
    TypologieLogementFoyerResidence,
)
from programmes.models.choices import Financement


class LotLgtsOptionForm(forms.Form):
    """
    Options liées à la déclaration des logements des conventions HLM, SEM, Type I & 2
    """

    uuid = forms.UUIDField(
        required=False,
        label="Logement du programme",
    )
    financement = forms.TypedChoiceField(
        required=False, label="", choices=Financement.choices
    )
    lgts_mixite_sociale_negocies = forms.IntegerField(
        required=False,
        label=(
            "Nombre de logements à louer en plus à des ménages dont les ressources"
            + " n'excèdent pas le plafond"
        ),
        help_text="""
            Plafond fixé au I de l'article D. 331-12. Ce nombre de logements doit-être
            négocié avec les services instructeurs. Il sera
            reporté sur l'article de mixité sociale correspondant su le document de convention.
        """,
    )
    loyer_derogatoire = forms.DecimalField(
        required=False,
        label="Loyer dérogatoire",
        help_text="""
            Montant de loyer d'une opération d'acquisition qui n'est pas liée à la réalisation
            de travaux mais fait suite à une nouvelle acquisition pour un locataire
            ou un occupant de bonne foi dont les ressources excèdent
            les plafonds de ressources par dérogation et à titre transitoire
        """,
        max_digits=6,
        decimal_places=2,
        error_messages={
            "max_digits": "Le loyer dérogatoire par m² doit-être inférieur à 10000 €",
        },
    )
    surface_locaux_collectifs_residentiels = forms.DecimalField(
        required=False,
        label="Surface des locaux collectifs résidentiels",
        max_digits=9,
        decimal_places=2,
        error_messages={
            "max_digits": """
                La surface des locaux collectifs
                résidentiels doit-être inférieure à 100000 m²
            """,
        },
    )
    loyer_associations_foncieres = forms.DecimalField(
        required=False,
        label="Montant du loyer pour les associations foncières et leurs filiales",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "max_digits": "Le montant du loyer  par m² pour les associations foncières doit être inférieur à 10000€",
        },
    )
    nb_logements = forms.IntegerField(
        label="Nombre de logements",
        error_messages={
            "required": "Le nombre de logements est obligatoire",
        },
    )
    formset_sans_loyer_disabled = forms.BooleanField(
        required=False,
    )
    formset_disabled = forms.BooleanField(
        required=False,
    )
    formset_corrigee_disabled = forms.BooleanField(
        required=False,
    )
    formset_corrigee_sans_loyer_disabled = forms.BooleanField(
        required=False,
    )


class LotFoyerResidenceLgtsDetailsForm(forms.Form):
    """
    Options liées à la déclaration des logements des conventions de type Foyer & Résidence
    """

    # floor_surface_habitable_totale (somme des surface habitables des logements déclarés)
    # est assigné au formuliaire avant sa validation.
    floor_surface_habitable_totale: float

    uuid = forms.UUIDField(
        required=False,
        label="Logement du programme",
    )
    surface_habitable_totale = forms.DecimalField(
        label="Surface habitable totale en m²",
        help_text="concerne la surface habitable de tout le bâti, y compris les locaux"
        + " auxquels ne s’applique pas la convention",
        max_digits=7,
        decimal_places=2,
        error_messages={
            "required": "La surface habitable totale est obligatoire",
            "max_digits": "La surface habitable doit-être inférieur à 100000 m²",
        },
    )
    nb_logements = forms.IntegerField(
        label="Nombre de logements",
        error_messages={
            "required": "Le nombre de logements est obligatoire",
        },
    )

    def clean_surface_habitable_totale(self):
        """
        Vérifie que la surface habitable totale du batiment est supérieur à la somme des
        surfaces des logements
        """
        surface_habitable_totale = self.cleaned_data.get("surface_habitable_totale", 0)
        if surface_habitable_totale < self.floor_surface_habitable_totale:
            raise ValidationError(
                "La surface habitable ne peut-être inférieur à la somme des surfaces"
                + f" habitables des logements ({self.floor_surface_habitable_totale} m²)"
            )

        return surface_habitable_totale


class BaseLogementForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
        label="Logement",
    )
    designation = forms.CharField(
        label="",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "La designation du logement est obligatoire",
            "min_length": "La designation du logement est obligatoire",
            "max_length": "La designation du logement ne doit pas excéder 255 caractères",
        },
    )
    financement = forms.TypedChoiceField(
        required=False, label="", choices=Financement.choices
    )

    typologie = forms.TypedChoiceField(
        required=True,
        label="",
        choices=TypologieLogementClassique.choices,
        error_messages={
            "required": "Le type de logement est obligatoire",
        },
    )
    surface_habitable = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface habitable est obligatoire",
            "max_digits": "La surface habitable doit-être inférieur à 10000 m²",
        },
    )
    import_order = forms.IntegerField(
        label="",
        required=False,
    )


class LogementCorrigeeSansLoyerForm(BaseLogementForm):
    surface_corrigee = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface corrigée est obligatoire",
            "max_digits": "La surface corrigée doit-être inférieur à 10000 m²",
        },
    )


class LogementCorrigeeForm(LogementCorrigeeSansLoyerForm):
    loyer_par_metre_carre = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer par m² est obligatoire",
            "max_digits": "La loyer par m² doit-être inférieur à 10000 €",
        },
    )
    coeficient = forms.DecimalField(
        required=True,
        label="",
        max_digits=6,
        decimal_places=4,
        error_messages={
            "required": "Le coefficient est obligatoire",
            "max_digits": "La coefficient doit-être inférieur à 1000",
        },
    )
    loyer = forms.DecimalField(
        required=True,
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
        Vérifcations:
        - le loyer doit-être le produit de la surface utile, du loyer par mètre carré et
          du coefficient (tolérance de 1 €)
        """
        surface_corrigee = self.cleaned_data.get("surface_corrigee", 0)
        loyer_par_metre_carre = self.cleaned_data.get("loyer_par_metre_carre", 0)
        coeficient = self.cleaned_data.get("coeficient", 0)
        loyer = self.cleaned_data.get("loyer", 0)

        if (
            abs(
                round_half_up(loyer, 2)
                - round_half_up(
                    surface_corrigee * loyer_par_metre_carre * coeficient, 2
                )
            )
            > 1
        ):
            raise ValidationError(
                "Le loyer doit-être le produit de la surface corrigée,"
                + " du loyer par mètre carré et du coefficient. valeur attendue :"
                + f" {round_half_up(surface_corrigee*loyer_par_metre_carre*coeficient,2)} €"
                + " (tolérance de 1 €)"
            )

        return loyer


class LogementSansLoyerForm(BaseLogementForm):
    """
    Formulaire Logement formant la liste des logements d'une convention de type HLM,
    SEM, type I & 2 : une ligne du tableau des logements par surface réelle sans loyers
    """

    surface_annexes = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface des annexes est obligatoire",
            "max_digits": "La surface des annexes doit-être inférieur à 10000 m²",
        },
    )
    surface_annexes_retenue = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface des annexes retenue est obligatoire",
            "max_digits": "La surface des annexes retenue doit-être inférieur à 10000 m²",
        },
    )
    surface_utile = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface utile est obligatoire",
            "max_digits": "La surface utile doit-être inférieur à 10000 m²",
        },
    )


class LogementForm(LogementSansLoyerForm):
    """
    Formulaire Logement formant la liste des logements d'une convention de type HLM,
    SEM, type I & 2 : une ligne du tableau des logements
    """

    loyer_par_metre_carre = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer par m² est obligatoire",
            "max_digits": "La loyer par m² doit-être inférieur à 10000 €",
        },
    )
    coeficient = forms.DecimalField(
        required=True,
        label="",
        max_digits=6,
        decimal_places=4,
        error_messages={
            "required": "Le coefficient est obligatoire",
            "max_digits": "La coefficient doit-être inférieur à 1000",
        },
    )
    loyer = forms.DecimalField(
        required=True,
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
        Vérifcations:
        - le loyer doit-être le produit de la surface utile, du loyer par mètre carré et
          du coefficient (tolérance de 1 €)
        """
        surface_utile = self.cleaned_data.get("surface_utile", 0)
        loyer_par_metre_carre = self.cleaned_data.get("loyer_par_metre_carre", 0)
        coeficient = self.cleaned_data.get("coeficient", 0)
        loyer = self.cleaned_data.get("loyer", 0)

        if (
            abs(
                round_half_up(loyer, 2)
                - round_half_up(surface_utile * loyer_par_metre_carre * coeficient, 2)
            )
            > 1
        ):
            raise ValidationError(
                "Le loyer doit-être le produit de la surface utile,"
                + " du loyer par mètre carré et du coefficient. valeur attendue :"
                + f" {round_half_up(surface_utile*loyer_par_metre_carre*coeficient,2)} €"
                + " (tolérance de 1 €)"
            )

        return loyer


class BaseLogementFormSet(BaseFormSet):
    """
    Ensemble des formulaires 'Logement' formant la liste des logements d'une convention
    de type HLM, SEM, type I & 2
    """

    # les champs suivants sont utilisés pour la validation des données
    # ils sont initialisés avant la validation
    programme_id: int = None
    lot_id: int = None
    nb_logements: int = None
    total_nb_logements: dict[str, int] | None = None
    optional_errors: list = []
    ignore_optional_errors = False

    def is_valid(self):
        return super().is_valid() and len(self.optional_errors) == 0

    def clean(self):
        self.manage_designation_validation()
        self.manage_same_loyer_par_metre_carre()
        self.manage_edd_consistency()
        self.manage_coefficient_propre()

        if self.ignore_optional_errors:
            return
        self.optional_errors = []
        self.manage_nb_logement_consistency()

    def manage_designation_validation(self):
        """
        Validation: les designations de logement doivent être uniques par convention
        """
        designations = {}
        error_on_designation = False
        for form in self.forms:
            designation = form.cleaned_data.get("designation")
            if designation:
                if designation in designations:
                    error_on_designation = True
                    form.add_error(
                        "designation",
                        "Les designations de logement doivent être uniques",
                    )
                    if "designation" not in designations[designation].errors:
                        designations[designation].add_error(
                            "designation",
                            "Les designations de logement doivent être uniques",
                        )
                designations[designation] = form
        if error_on_designation:
            error = ValidationError("Les designations de logement doivent être uniques")
            self._non_form_errors.append(error)

    def manage_same_loyer_par_metre_carre(self):
        """
        Validation: le loyer par mètre carré doit être le même pour tous les logements du lot
        """
        lpmc = None
        error = None
        for form in self.forms:
            if lpmc is None:
                lpmc = form.cleaned_data.get("loyer_par_metre_carre")
            elif (
                lpmc != form.cleaned_data.get("loyer_par_metre_carre") and error is None
            ):
                error = ValidationError(
                    "Le loyer par mètre carré doit être le même pour tous les logements du lot"
                )
                self._non_form_errors.append(error)
        if error is not None:
            for form in self.forms:
                form.add_error(
                    "loyer_par_metre_carre",
                    "Le loyer par mètre carré doit être le même pour tous les logements du lot",
                )

    def manage_edd_consistency(self):
        """
        Validation: les logements déclarés dans l'EDD simplifié pour le financement de la
          convention doivent être déclarés dans la convention
        """
        lgts_edd = LogementEDD.objects.filter(programme_id=self.programme_id)
        lot = Lot.objects.get(id=self.lot_id)

        if lgts_edd.count() != 0:
            for form in self.forms:
                try:
                    lgt_edd = lgts_edd.get(
                        designation=form.cleaned_data.get("designation"),
                        financement=lot.financement,
                    )
                    if lgt_edd.financement != lot.financement:
                        form.add_error(
                            "designation",
                            "Ce logement est déclaré comme "
                            + f"{lgt_edd.financement} dans l'EDD simplifié "
                            + "alors que vous déclarez un lot de type "
                            + f"{lot.financement}",
                        )
                except LogementEDD.DoesNotExist:
                    form.add_error(
                        "designation", "Ce logement n'est pas dans l'EDD simplifié"
                    )
                except LogementEDD.MultipleObjectsReturned:
                    form.add_error(
                        "designation",
                        "Ce logement est présent plusieurs fois dans l'EDD simplifié",
                    )

    def manage_nb_logement_consistency(self):
        """
        Validation: le nombre de logements déclarés pour cette convention à l'étape Opération
          doit correspondre au nombre de logements de la liste à l'étape Logements
        """
        for financement in self.total_nb_logements:
            if self.nb_logements != self.total_nb_logements[financement]:
                error = ValidationError(
                    f"Le nombre de logement à conventionner ({self.nb_logements}) "
                    + f"ne correspond pas au nombre de logements déclaré ({self.total_nb_logements[financement]})"
                )
                self.optional_errors.append(error)

    def manage_coefficient_propre(self):
        """
        Validation: La somme des loyers après application des coefficients ne peut excéder
          la somme des loyers sans application des coefficients (tolérence de 1 € par logement)
        """
        loyer_with_coef = 0
        loyer_without_coef = 0
        for form in self.forms:
            coeficient = form.cleaned_data.get("coeficient")
            surface_utile = form.cleaned_data.get("surface_utile")
            loyer_par_metre_carre = form.cleaned_data.get("loyer_par_metre_carre")
            if None in [coeficient, surface_utile, loyer_par_metre_carre]:
                # Another error is catch before and need to be managed before
                return
            loyer_with_coef += coeficient * surface_utile * loyer_par_metre_carre
            loyer_without_coef += surface_utile * loyer_par_metre_carre
        if (
            self.nb_logements is not None
            and round_half_up(loyer_with_coef, 2)
            > round_half_up(loyer_without_coef, 2) + self.nb_logements
        ):
            error = ValidationError(
                "La somme des loyers après application des coefficients ne peut excéder "
                + "la somme des loyers sans application des coefficients, c'est à dire "
                + f"{round_half_up(loyer_without_coef,2)} € (tolérance de {self.nb_logements} €)"
            )
            self._non_form_errors.append(error)


LogementFormSet = formset_factory(LogementForm, formset=BaseLogementFormSet, extra=0)
LogementSansLoyerFormSet = formset_factory(
    LogementSansLoyerForm, formset=BaseLogementFormSet, extra=0
)
LogementCorrigeeFormSet = formset_factory(
    LogementCorrigeeForm, formset=BaseLogementFormSet, extra=0
)
LogementCorrigeeSansLoyerFormSet = formset_factory(
    LogementCorrigeeSansLoyerForm, formset=BaseLogementFormSet, extra=0
)
LotLgtsOptionFormSet = formset_factory(LotLgtsOptionForm, extra=0)


class FoyerResidenceLogementForm(forms.Form):
    """
    Formulaire Logement formant la liste des logements d'une convention de type Foyer & Résidence :
      une ligne du tableau des logements
    """

    uuid = forms.UUIDField(
        required=False,
        label="Logement",
    )
    designation = forms.CharField(
        label="",
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le numéro du logement du logement est obligatoire",
            "min_length": "Le numéro du logement du logement est obligatoire",
            "max_length": "Le numéro du logement du logement ne doit pas excéder 255 caractères",
        },
    )
    typologie = forms.TypedChoiceField(
        required=True,
        label="",
        choices=TypologieLogementFoyerResidence.choices,
        error_messages={
            "required": "Le type de logement est obligatoire",
        },
    )
    surface_habitable = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface habitable est obligatoire",
            "max_digits": "La surface habitable doit-être inférieur à 10000 m²",
        },
    )
    loyer = forms.DecimalField(
        label="",
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La redevance maximale est obligatoire",
            "max_digits": "La redevance maximale inférieur à 10000 €",
        },
    )
    import_order = forms.IntegerField(
        label="",
        required=False,
    )


class BaseFoyerResidenceLogementFormSet(BaseFormSet):
    """
    Ensemble des formulaires 'Logement' formant la liste des logements d'une convention
      de type Foyer & Résidence
    """

    # les champs suivants sont utilisés pour la validation des données
    # ils sont initialisés avant la validation
    nb_logements: int = None
    optional_errors: list = []
    ignore_optional_errors = False

    def is_valid(self):
        return super().is_valid() and len(self.optional_errors) == 0

    def clean(self):
        self.loan_should_be_consistent()

        if self.ignore_optional_errors:
            return
        self.optional_errors = []
        self.manage_nb_logement_consistency()

    def manage_nb_logement_consistency(self):
        """
        Validation: le nombre de logements déclarés pour cette convention à l'étape Opération
          doit correspondre au nombre de logements de la liste à l'étape Logements
        """
        if self.nb_logements != self.total_form_count():
            error = ValidationError(
                f"Le nombre de logement à conventionner ({self.nb_logements}) "
                + f"ne correspond pas au nombre de logements déclaré ({self.total_form_count()})"
            )
            self.optional_errors.append(error)

    def loan_should_be_consistent(self):
        """
        Validation: les loyers doivent-être identiques pour les logements de typologie identique
        """
        loan_by_type = {}
        loan_errors = {}
        for form in self.forms:
            typologie = form.cleaned_data.get("typologie", "")
            if typologie not in loan_by_type:
                loan_by_type[typologie] = form.cleaned_data.get("loyer")
            else:
                if loan_by_type[typologie] != form.cleaned_data.get("loyer"):
                    loan_errors[typologie] = ValidationError(
                        "Les loyers doivent-être identiques pour les logements de"
                        + f" typologie identique : {form.cleaned_data.get('typologie')}"
                    )
        for _, loan_error in loan_errors.items():
            self._non_form_errors.append(loan_error)


FoyerResidenceLogementFormSet = formset_factory(
    FoyerResidenceLogementForm,
    formset=BaseFoyerResidenceLogementFormSet,
    extra=0,
)
