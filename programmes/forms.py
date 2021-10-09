from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory
from core import forms_utils

from programmes.models import (
    LogementEDD,
    Lot,
    TypeHabitat,
    TypologieLogement,
    TypologieAnnexe,
    TypologieStationnement,
)
from conventions.models import Financement


class ProgrammeSelectionForm(forms.Form):
    lot_uuid = forms.CharField(
        error_messages={
            "required": "La selection du programme et de son financement est obligatoire"
        }
    )

    def clean_lot_uuid(self):
        lot_uuid = self.cleaned_data["lot_uuid"]

        # check that lot_id exist in DB
        if not Lot.objects.get(uuid=lot_uuid):
            raise ValidationError("le programme avec ce financement n'existe pas")

        return lot_uuid


class ProgrammeForm(forms.Form):
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
    type_operation = forms.CharField(required=False)
    anru = forms.BooleanField(required=False)
    nb_locaux_commerciaux = forms.IntegerField(required=False)
    nb_bureaux = forms.IntegerField(required=False)
    autre_locaux_hors_convention = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "L'information ne doit pas excéder 5000 characters",
        },
    )


class ProgrammeCadastralForm(forms.Form):
    permis_construire = forms.CharField(required=False)
    date_acte_notarie = forms.DateField(required=False)
    date_achevement_previsible = forms.DateField(required=False)
    date_achat = forms.DateField(required=False)
    date_achevement = forms.DateField(required=False)
    vendeur = forms.CharField(
        required=True,
        max_length=5000,
        error_messages={
            "required": "Les informations relatives au vendeur sont obligatoires",
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
        help_text="Identité du vendeur telle que mentionnée dans l'acte de propriété",
    )
    vendeur_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    acquereur = forms.CharField(
        required=True,
        max_length=5000,
        error_messages={
            "required": "Les informations relatives à l'aquéreur sont obligatoires",
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


class ReferenceCadastraleForm(forms.Form):
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

    edd_volumetrique = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "L'EDD volumétrique ne doit pas excéder 5000 characters",
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
    )

    edd_classique = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "L'EDD classique ne doit pas excéder 5000 characters",
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
        decimal_places=3,
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
        surface_utile = self.cleaned_data["surface_utile"]
        loyer_par_metre_carre = self.cleaned_data["loyer_par_metre_carre"]
        coeficient = self.cleaned_data["coeficient"]
        loyer = self.cleaned_data["loyer"]

        # check that lot_id exist in DB
        if round(loyer, 2) != round(
            surface_utile * loyer_par_metre_carre * coeficient, 2
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
                if designation in designations.keys():
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
            elif lpmc != form.cleaned_data.get("loyer_par_metre_carre"):
                error = ValidationError(
                    "Le loyer par mètre carré doit être le même pour tous les logements du lot"
                )
                self._non_form_errors.append(error)
        if error is not None:
            for form in self.forms:
                form.add_error("loyer_par_metre_carre", "non conforme")

    def manage_edd_consistency(self):
        lgts_edd = LogementEDD.objects.filter(programme_id=self.programme_id)
        if lgts_edd.count() != 0:
            for form in self.forms:
                try:
                    lgts_edd.get(designation=form.cleaned_data.get("designation"))
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


LogementFormSet = formset_factory(LogementForm, formset=BaseLogementFormSet, extra=0)


class AnnexeForm(forms.Form):

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
    pass


AnnexeFormSet = formset_factory(AnnexeForm, formset=BaseAnnexeFormSet, extra=0)


class TypeStationnementForm(forms.Form):

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
    pass


LogementEDDFormSet = formset_factory(
    LogementEDDForm, formset=BaseLogementEDDFormSet, extra=0
)
