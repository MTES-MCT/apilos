from django import forms
from django.forms import formset_factory
from django.forms.fields import FileField

from .models import Preteur

class ConventionCommentForm(forms.Form):

  comments = forms.CharField(required=False, max_length=5000, error_messages={
    'max_length':"Le message ne doit pas excéder 5000 characters",
    })

class ConventionFinancementForm(forms.Form):

  date_fin_conventionnement = forms.DateField(required=False)

class PretForm(forms.Form):

  numero = forms.CharField(required=True, max_length=255, error_messages={
    'required': "Le numero de prêt est obligatoire",
    'max_length': "Le numero ne doit pas excéder 255 characters",
    })
  preteur = forms.TypedChoiceField(required=False, choices=Preteur.choices)
  autre = forms.CharField(required=False, max_length=255, error_messages={
    'max_length': "Le prêteur ne doit pas excéder 255 characters",
    })
  date_octroi = forms.DateField(required=False)
  duree = forms.IntegerField(required=False)
  montant = forms.FloatField(error_messages={
    'required': "Le montant du prêt est obligatoire",
    })

PretFormSet = formset_factory(PretForm, extra=0)

class UploadForm(forms.Form):

  file = FileField()