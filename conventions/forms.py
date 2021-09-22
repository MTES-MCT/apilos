from django import forms
from django.forms import BaseFormSet, formset_factory
from django.forms.fields import FileField
from django.core.exceptions import ValidationError

from .models import Preteur


class ConventionCommentForm(forms.Form):

    comments = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 characters",
        },
    )


class ConventionFinancementForm(forms.Form):

    date_fin_conventionnement = forms.DateField(
        error_messages={
            "required": "La date de fin de conventionnement est obligatoire",
        }
    )
    fond_propre = forms.FloatField(required=False)


class PretForm(forms.Form):

    numero = forms.CharField(
        required=False,
        max_length=255,
        error_messages={
            "max_length": "Le numero ne doit pas excéder 255 characters",
        },
    )
    preteur = forms.TypedChoiceField(required=False, choices=Preteur.choices)
    autre = forms.CharField(
        required=False,
        max_length=255,
        error_messages={
            "max_length": "Le prêteur ne doit pas excéder 255 characters",
        },
    )
    date_octroi = forms.DateField(required=False)
    duree = forms.IntegerField(required=False)
    montant = forms.FloatField(
        error_messages={
            "required": "Le montant du prêt est obligatoire",
        }
    )

    def clean(self):
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
                    ("Le numéro est obligatoire pour un prêt" +
                    " de la Caisse de dépôts et consignations"),
                )
        if preteur in ["AUTRE"]:
            if not cleaned_data.get("autre"):
                self.add_error("autre", "Merci de préciser le prêteur")


class BasePretFormSet(BaseFormSet):
    def clean(self):
        self.manage_cdc_validation()

    def manage_cdc_validation(self):
        for form in self.forms:
            #            if self.can_delete() and self._should_delete_form(form):
            #                continue
            if form.cleaned_data.get("preteur") in ["CDCF", "CDCL"]:
                return
        error = ValidationError(
            "Au moins un prêt à la Caisee des dépôts et consignations doit-être déclaré "
            + "(CDC foncière, CDC locative)"
        )
        self._non_form_errors.append(error)


PretFormSet = formset_factory(PretForm, formset=BasePretFormSet, extra=0)


class UploadForm(forms.Form):

    file = FileField(
        error_messages={
            "required": ("Vous devez séléctionner un fichier avant " +
            "de cliquer sur le bouton 'Téléverser'"),
        }
    )
