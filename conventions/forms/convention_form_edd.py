"""
Étape EDD (État descriptif des divisions) du formulaire par étape de la convention
"""

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from programmes.models import FinancementEDD, Lot


class ProgrammeEDDForm(forms.Form):
    """
    Formulaire définissant les informations générales de l'EDD liées à une convention
    """

    uuid = forms.UUIDField(
        required=False,
        label="Logement du programme",
    )
    lot_uuid = forms.UUIDField(required=False)
    edd_volumetrique = forms.CharField(
        required=False,
        label="EDD volumétrique",
        max_length=50000,
        error_messages={
            "max_length": "L'EDD volumétrique ne doit pas excéder 50000 caractères",
        },
    )
    edd_volumetrique_files = forms.CharField(
        required=False,
    )
    mention_publication_edd_volumetrique = forms.CharField(
        required=False,
        label="Mention de publication de l'EDD volumétrique",
        max_length=5000,
        error_messages={
            "max_length": "La mention de publication de l'EDD volumétrique "
            + "ne doit pas excéder 1000 caractères",
        },
        help_text=(
            "Référence légale de dépôt de l'état descriptif de division "
            + "volumétrique aux services de la publicité foncière comportant "
            + "le numéro, le service, la date et les volumes du dépôt"
        ),
    )
    edd_classique = forms.CharField(
        required=False,
        label="EDD classique",
        max_length=50000,
        error_messages={
            "max_length": "L'EDD classique ne doit pas excéder 50000 caractères",
        },
    )
    edd_classique_files = forms.CharField(
        required=False,
    )
    mention_publication_edd_classique = forms.CharField(
        required=False,
        label="Mention de publication de l'EDD classique",
        max_length=5000,
        error_messages={
            "max_length": "La mention de publication de l'EDD classique "
            + "ne doit pas excéder 1000 caractères",
        },
        help_text=(
            "Référence légale de dépôt de l'état descriptif de division "
            + "classique aux services de la publicité foncière comportant "
            + "le numéro, le service, la date et les volumes du dépôt"
        ),
    )
    edd_stationnements = forms.CharField(
        required=False,
        label="EDD pour les stationnements",
        max_length=50000,
        error_messages={
            "max_length": "L'EDD pour les stationnements ne doit pas excéder 50000 caractères",
        },
    )
    edd_stationnements_files = forms.CharField(
        required=False,
    )


class LogementEDDForm(forms.Form):

    uuid = forms.UUIDField(required=False, label="Logement de l'EDD")
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
    numero_lot = forms.CharField(
        label="",
        max_length=255,
        min_length=1,
        error_messages={
            "max_length": "Le numéro de lot ne doit pas excéder 255 caractères",
        },
    )
    financement = forms.TypedChoiceField(
        required=True,
        label="",
        choices=FinancementEDD.choices,
        error_messages={
            "required": "Le financement est obligatoire",
        },
    )


class BaseLogementEDDFormSet(BaseFormSet):
    """
    Liste des formulaires définissant les logements de l'EDD liés à une convention:
      tableau des logement dans l'EDD simplifié
    """

    # Ces attributs sont définis avant la validation du formulaire
    programme_id = None
    optional_errors = []
    ignore_optional_errors = False

    def is_valid(self):
        return super().is_valid() and len(self.optional_errors) == 0

    def clean(self):
        self.manage_edd_consistency()

    def manage_edd_consistency(self):
        """
        Validation: l'EDD simplifié doit comporter tous les logement de tous les types
         de financement du programme il est possible de passr outre cette validation
         (cf. ignore_optional_errors)
        """
        self.optional_errors = []
        if len(self.forms) == 0 or self.ignore_optional_errors:
            return
        lots = Lot.objects.filter(convention__programme_id=self.programme_id)
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
