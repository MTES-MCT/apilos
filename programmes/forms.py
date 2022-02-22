from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory
from core import forms_utils

from programmes.models import (
    Logement,
    LogementEDD,
    Lot,
    TypeHabitat,
    TypeOperation,
    TypologieLogement,
    TypologieAnnexe,
    TypologieStationnement,
)
from conventions.models import Financement


class ProgrammeSelectionForm(forms.Form):
    lot_uuid = forms.CharField(
        required=False,
        error_messages={
            "required": "La selection du programme et de son financement est obligatoire"
        },
    )

    existing_programme = forms.ChoiceField(
        choices=[("selection", "selection"), ("creation", "creation")]
    )
    bailleur = forms.IntegerField(required=False)
    nom = forms.CharField(
        required=False,
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le nom du programme est obligatoire",
            "min_length": "Le nom du programme est obligatoire",
            "max_length": "Le nom du programme ne doit pas excéder 255 caractères",
        },
    )
    nb_logements = forms.IntegerField(
        required=False,
        error_messages={
            "required": "Le nombre de logements à conventionner est obligatoire",
        },
    )
    type_habitat = forms.TypedChoiceField(
        required=False,
        choices=TypeHabitat.choices,
        error_messages={
            "required": "Le type d'habitat est obligatoire",
        },
    )
    financement = forms.TypedChoiceField(
        required=False,
        choices=Financement.choices,
        error_messages={
            "required": "Le financement est obligatoire",
        },
    )
    code_postal = forms.CharField(
        required=False,
        max_length=255,
        error_messages={
            "required": "Le code postal est obligatoire",
            "max_length": "Le code postal ne doit pas excéder 255 caractères",
        },
    )
    ville = forms.CharField(
        required=False,
        max_length=255,
        error_messages={
            "required": "La ville est obligatoire",
            "max_length": "La ville ne doit pas excéder 255 caractères",
        },
    )

    def validate_required_field(self, cleaned_data, field_name):
        if field_name in cleaned_data and (
            cleaned_data[field_name] is None or cleaned_data[field_name] == ""
        ):
            self._errors[field_name] = self.error_class(
                [self.fields[field_name].error_messages["required"]]
            )
            del cleaned_data[field_name]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["existing_programme"] == "selection":
            self.validate_required_field(cleaned_data, "lot_uuid")
        if cleaned_data["existing_programme"] == "creation":
            self.validate_required_field(cleaned_data, "bailleur")
            self.validate_required_field(cleaned_data, "nom")
            self.validate_required_field(cleaned_data, "nb_logements")
            self.validate_required_field(cleaned_data, "financement")
            self.validate_required_field(cleaned_data, "type_habitat")
            self.validate_required_field(cleaned_data, "code_postal")
            self.validate_required_field(cleaned_data, "ville")


class ProgrammeForm(forms.Form):
    object_name = "programme"

    uuid = forms.UUIDField(required=False)
    nom = forms.CharField(
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le nom du programme est obligatoire",
            "min_length": "Le nom du programme est obligatoire",
            "max_length": "Le nom du programme ne doit pas excéder 255 caractères",
        },
    )
    adresse, code_postal, ville = forms_utils.address_form_fields()
    nb_logements = forms.IntegerField(
        error_messages={
            "required": "Le nombre de logements à conventionner est obligatoire",
        },
    )
    type_habitat = forms.TypedChoiceField(required=False, choices=TypeHabitat.choices)
    type_operation = forms.TypedChoiceField(
        required=False, choices=TypeOperation.choices
    )
    anru = forms.BooleanField(required=False)
    nb_locaux_commerciaux = forms.IntegerField(required=False)
    nb_bureaux = forms.IntegerField(required=False)
    autres_locaux_hors_convention = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "L'information ne doit pas excéder 5000 characters",
        },
    )


class ProgrammeCadastralForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    permis_construire = forms.CharField(required=False)
    date_acte_notarie = forms.DateField(required=False)
    date_achevement_previsible = forms.DateField(required=False)
    date_achat = forms.DateField(required=False)
    date_achevement = forms.DateField(required=False)
    vendeur = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
        help_text="Identité du vendeur telle que mentionnée dans l'acte de propriété",
    )
    vendeur_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    acquereur = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
        help_text="Identité de l'acquéreur telle que mentionnée dans l'acte de propriété",
    )
    acquereur_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    reference_notaire = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
    )
    reference_notaire_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    reference_publication_acte = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
    )
    reference_publication_acte_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    acte_de_propriete = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
    )
    acte_de_propriete_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )
    acte_notarial = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
    )
    acte_notarial_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )
    reference_cadastrale = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
    )
    reference_cadastrale_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )


class ReferenceCadastraleForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    section = forms.CharField(
        required=True,
        max_length=255,
        error_messages={
            "required": "La section est obligatoire",
            "max_length": "Le message ne doit pas excéder 255 characters",
        },
    )
    numero = forms.IntegerField(
        error_messages={
            "required": "Le numéro est obligatoire",
        },
    )
    lieudit = forms.CharField(
        required=True,
        max_length=255,
        error_messages={
            "required": "Le lieudit est obligatoire",
            "max_length": "Le lieudit ne doit pas excéder 255 characters",
        },
    )
    surface = forms.CharField(
        required=True,
        max_length=255,
        error_messages={
            "required": "La surface est obligatoire",
            "max_length": "La surface ne doit pas excéder 255 characters",
        },
    )


class BaseReferenceCadastraleFormSet(BaseFormSet):
    pass


ReferenceCadastraleFormSet = formset_factory(
    ReferenceCadastraleForm, formset=BaseReferenceCadastraleFormSet, extra=0
)


class ProgrammeEDDForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    lot_uuid = forms.UUIDField(required=False)
    edd_volumetrique = forms.CharField(
        required=False,
        max_length=50000,
        error_messages={
            "max_length": "L'EDD volumétrique ne doit pas excéder 50000 characters",
        },
    )
    edd_volumetrique_files = forms.CharField(
        required=False,
    )
    mention_publication_edd_volumetrique = forms.CharField(
        required=False,
        max_length=1000,
        error_messages={
            "max_length": "La mention de publication de l'EDD volumétrique "
            + "ne doit pas excéder 1000 characters",
        },
        help_text=(
            "Référence légale de dépôt de l'état descriptif de division "
            + "volumétrique aux services des hypothèques comportant "
            + "le numéro, le service, la date et les volumes du dépôt"
        ),
    )
    edd_classique = forms.CharField(
        required=False,
        max_length=50000,
        error_messages={
            "max_length": "L'EDD classique ne doit pas excéder 50000 characters",
        },
    )
    edd_classique_files = forms.CharField(
        required=False,
    )
    mention_publication_edd_classique = forms.CharField(
        required=False,
        max_length=1000,
        error_messages={
            "max_length": "La mention de publication de l'EDD classique "
            + "ne doit pas excéder 1000 characters",
        },
        help_text=(
            "Référence légale de dépôt de l'état descriptif de division "
            + "classique aux services des hypothèques comportant "
            + "le numéro, le service, la date et les volumes du dépôt"
        ),
    )


class LogementForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    designation = forms.CharField(
        max_length=255,
        min_length=1,
        error_messages={
            "required": "La designation du logement est obligatoire",
            "min_length": "La designation du logement est obligatoire",
            "max_length": "La designation du logement ne doit pas excéder 255 caractères",
        },
    )
    typologie = forms.TypedChoiceField(
        required=True,
        choices=TypologieLogement.choices,
        error_messages={
            "required": "Le type de logement est obligatoire",
        },
    )
    surface_habitable = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface habitable est obligatoire",
            "max_digits": "La surface habitable doit-être inférieur à 10000 m²",
        },
    )
    surface_annexes = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface des annexes est obligatoire",
            "max_digits": "La surface des annexes doit-être inférieur à 10000 m²",
        },
    )
    surface_annexes_retenue = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface des annexes retenue est obligatoire",
            "max_digits": "La surface des annexes retenue doit-être inférieur à 10000 m²",
        },
    )
    surface_utile = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface utile est obligatoire",
            "max_digits": "La surface utile doit-être inférieur à 10000 m²",
        },
    )
    loyer_par_metre_carre = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer par m² est obligatoire",
            "max_digits": "La loyer par m² doit-être inférieur à 10000 €",
        },
    )
    coeficient = forms.DecimalField(
        max_digits=6,
        decimal_places=4,
        error_messages={
            "required": "Le coéficient est obligatoire",
            "max_digits": "La coéficient doit-être inférieur à 1000",
        },
    )
    loyer = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer est obligatoire",
            "max_digits": "La loyer doit-être inférieur à 10000 €",
        },
    )

    def clean_loyer(self):
        surface_utile = self.cleaned_data.get("surface_utile", 0)
        loyer_par_metre_carre = self.cleaned_data.get("loyer_par_metre_carre", 0)
        coeficient = self.cleaned_data.get("coeficient", 0)
        loyer = self.cleaned_data.get("loyer", 0)

        # check that lot_id exist in DB
        if (
            abs(
                round(loyer, 2)
                - round(surface_utile * loyer_par_metre_carre * coeficient, 2)
            )
            > 0.04
        ):
            raise ValidationError(
                "Le loyer doit-être le produit de la surface utile, "
                + "du loyer par mètre carré et du coéficient. "
                + f"valeur attendue : {round(surface_utile*loyer_par_metre_carre*coeficient,2)}"
            )

        return loyer


class BaseLogementFormSet(BaseFormSet):
    programme_id = None
    lot_id = None

    def clean(self):
        self.manage_non_empty_validation()
        self.manage_designation_validation()
        self.manage_same_loyer_par_metre_carre()
        self.manage_edd_consistency()
        self.manage_nb_logement_consistency()
        self.manage_coefficient_propre()

    def manage_non_empty_validation(self):
        if len(self.forms) == 0:
            error = ValidationError("La liste des logements ne peut pas être vide")
            self._non_form_errors.append(error)

    def manage_designation_validation(self):
        designations = {}
        error_on_designation = False
        for form in self.forms:
            #            if self.can_delete() and self._should_delete_form(form):
            #                continue
            designation = form.cleaned_data.get("designation")
            if designation:
                if designation in designations:
                    error_on_designation = True
                    form.add_error(
                        "designation",
                        "Les designations de logement doivent être distinct "
                        + "lorsqu'ils sont définis",
                    )
                    if "designation" not in designations[designation].errors:
                        designations[designation].add_error(
                            "designation",
                            "Les designations de logement doivent être distinct lorsqu'ils sont "
                            + "définis",
                        )
                designations[designation] = form
        if error_on_designation:
            error = ValidationError(
                "Les designations de logement doivent être distinct lorsqu'ils sont définis !!!"
            )
            self._non_form_errors.append(error)

    def manage_same_loyer_par_metre_carre(self):
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
        lgts_edd = LogementEDD.objects.filter(programme_id=self.programme_id)
        lot = Lot.objects.get(id=self.lot_id)

        if lgts_edd.count() != 0:
            for form in self.forms:
                try:
                    lgt_edd = lgts_edd.get(
                        designation=form.cleaned_data.get("designation")
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

    def manage_nb_logement_consistency(self):
        lot = Lot.objects.get(id=self.lot_id)
        if lot.nb_logements != self.total_form_count():
            error = ValidationError(
                f"Le nombre de logement a conventionner ({lot.nb_logements}) "
                + f"ne correspond pas au nombre de logements déclaré ({self.total_form_count()})"
            )
            self._non_form_errors.append(error)

    def manage_coefficient_propre(self):
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
        if round(loyer_with_coef, 2) > round(loyer_without_coef, 2):
            error = ValidationError(
                "La somme des loyers après application des coéficients ne peut excéder "
                + "la somme des loyers sans application des coéficients, c'est à dire "
                + f"{round(loyer_without_coef,2)} €"
            )
            self._non_form_errors.append(error)


LogementFormSet = formset_factory(LogementForm, formset=BaseLogementFormSet, extra=0)


class AnnexeForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    typologie = forms.TypedChoiceField(required=True, choices=TypologieAnnexe.choices)
    logement_designation = forms.CharField(
        max_length=255,
        min_length=1,
        error_messages={
            "required": "La designation du logement est obligatoire",
            "min_length": "La designation du logement est obligatoire",
            "max_length": "La designation du logement ne doit pas excéder 255 caractères",
        },
    )
    logement_typologie = forms.TypedChoiceField(
        required=True, choices=TypologieLogement.choices
    )
    surface_hors_surface_retenue = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "La surface habitable est obligatoire",
            "max_digits": "La surface habitable doit-être inférieur à 10000 m²",
        },
    )
    loyer_par_metre_carre = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer par m² est obligatoire",
            "max_digits": "La loyer par m² doit-être inférieur à 10000 €",
        },
    )
    loyer = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer est obligatoire",
            "max_digits": "La loyer doit-être inférieur à 10000 €",
        },
    )


class BaseAnnexeFormSet(BaseFormSet):
    convention = None

    def clean(self):
        self.manage_logement_exists_validation()

    def manage_logement_exists_validation(self):
        if self.convention:
            lgts = self.convention.lot.logement_set.all()
            for form in self.forms:
                try:
                    lgts.get(designation=form.cleaned_data.get("logement_designation"))
                except Logement.DoesNotExist:
                    form.add_error(
                        "logement_designation", "Ce logement n'existe pas dans ce lot"
                    )


AnnexeFormSet = formset_factory(AnnexeForm, formset=BaseAnnexeFormSet, extra=0)


class TypeStationnementForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    typologie = forms.TypedChoiceField(
        required=True,
        choices=TypologieStationnement.choices,
        error_messages={
            "required": "La typologie des stationnement est obligatoire",
        },
    )
    nb_stationnements = forms.IntegerField(
        error_messages={
            "required": "Le nombre de stationnements est obligatoire",
        },
    )
    loyer = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        error_messages={
            "required": "Le loyer est obligatoire",
            "max_digits": "La loyer doit-être inférieur à 10000 €",
        },
    )


class BaseTypeStationnementFormSet(BaseFormSet):
    pass


TypeStationnementFormSet = formset_factory(
    TypeStationnementForm, formset=BaseTypeStationnementFormSet, extra=0
)


class LogementEDDForm(forms.Form):

    uuid = forms.UUIDField(required=False)
    designation = forms.CharField(
        max_length=255,
        min_length=1,
        error_messages={
            "required": "La designation du logement est obligatoire",
            "min_length": "La designation du logement est obligatoire",
            "max_length": "La designation du logement ne doit pas excéder 255 caractères",
        },
    )
    typologie = forms.TypedChoiceField(
        required=True,
        choices=TypologieLogement.choices,
        error_messages={
            "required": "Le type de logement est obligatoire",
        },
    )
    financement = forms.TypedChoiceField(
        required=True,
        choices=Financement.choices,
        error_messages={
            "required": "Le financement est obligatoire",
        },
    )


class BaseLogementEDDFormSet(BaseFormSet):
    programme_id = None
    optional_errors = []
    ignore_optional_errors = False

    def is_valid(self):
        return super().is_valid() and len(self.optional_errors) == 0

    def clean(self):
        self.manage_edd_consistency()

    def manage_edd_consistency(self):
        self.optional_errors = []
        if len(self.forms) == 0 or self.ignore_optional_errors:
            return
        lots = Lot.objects.filter(programme_id=self.programme_id)
        programme_financements = list(set(map(lambda x: x.financement, lots)))
        lgts_edd_financements = list(
            set(map(lambda x: x.cleaned_data.get("financement"), self.forms))
        )
        for programme_financement in programme_financements:
            if programme_financement not in lgts_edd_financements:
                if len(programme_financements) > 1:
                    financement_message = (
                        "Les financements connus pour ce programme sont "
                        + ", ".join(programme_financements)
                    )
                else:
                    financement_message = (
                        "Le seul financement connu pour ce programme est "
                        + programme_financement
                    )

                error = ValidationError(
                    "L'EDD simplifié doit comporter tous les logements du "
                    + f"programme quelquesoit leur financement. {financement_message}",
                    code=101,
                )
                self.optional_errors.append(error)
                return


LogementEDDFormSet = formset_factory(
    LogementEDDForm, formset=BaseLogementEDDFormSet, extra=0
)


class LotAnnexeForm(forms.Form):
    uuid = forms.UUIDField(required=False)
    annexe_caves = forms.BooleanField(required=False)
    annexe_soussols = forms.BooleanField(required=False)
    annexe_remises = forms.BooleanField(required=False)
    annexe_ateliers = forms.BooleanField(required=False)
    annexe_sechoirs = forms.BooleanField(required=False)
    annexe_celliers = forms.BooleanField(required=False)
    annexe_resserres = forms.BooleanField(required=False)
    annexe_combles = forms.BooleanField(required=False)
    annexe_balcons = forms.BooleanField(required=False)
    annexe_loggias = forms.BooleanField(required=False)
    annexe_terrasses = forms.BooleanField(required=False)
