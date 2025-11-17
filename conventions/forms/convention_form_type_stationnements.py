"""
Étape Type de stationnement du formulaire par étape de la convention (type HLM, SEM, Type I & 2)
"""

from django import forms
from django.forms import BaseFormSet, formset_factory

from programmes.models import (
    TypologieStationnement,
)
from programmes.models.choices import Financement


class TypeStationnementForm(forms.Form):

    uuid = forms.UUIDField(
        required=False,
        label="Type de stationnement",
    )
    typologie = forms.TypedChoiceField(
        required=True,
        label="",
        choices=TypologieStationnement.choices,
        error_messages={
            "required": "La typologie des stationnement est obligatoire",
        },
    )
    financement = forms.TypedChoiceField(
        required=False, label="", choices=Financement.choices
    )
    nb_stationnements = forms.IntegerField(
        label="",
        error_messages={
            "required": "Le nombre de stationnements est obligatoire",
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


class BaseTypeStationnementFormSet(BaseFormSet):
    pass


TypeStationnementFormSet = formset_factory(
    TypeStationnementForm, formset=BaseTypeStationnementFormSet, extra=0
)
