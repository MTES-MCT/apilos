from django import forms
from django.core.exceptions import ValidationError

from programmes.models import Lot, TypeHabitat

class ProgrammeSelectionForm(forms.Form):
  lot_uuid = forms.CharField(error_messages={'required': 'La selection du programme et de son financement est obligatoire'})

  def clean_lot_uuid(self):
    lot_uuid = self.cleaned_data['lot_uuid']

    # check that lot_id exist in DB
    if not Lot.objects.get(uuid=lot_uuid):
      raise ValidationError("le programme avec ce financement n'existe pas")

    return lot_uuid

class ProgrammeForm(forms.Form):

  adresse = forms.CharField(max_length=255, min_length=1, error_messages={
    'required': "L'adresse est obligatoire",
    'min_length':"L'adresse est obligatoire",
    'max_length':"L'adresse ne doit pas excéder 255 caractères",
  })
  code_postal = forms.CharField(max_length=255, error_messages={
    'required': "Le code postal est obligatoire",
    'max_length':"Le code postal ne doit pas excéder 255 caractères",
  })
  ville = forms.CharField(max_length=255, error_messages={
    'required': "La ville est obligatoire",
    'max_length':"La ville ne doit pas excéder 255 caractères",
  })
  nb_logements = forms.IntegerField()
  type_habitat = forms.TypedChoiceField(required=False, choices=TypeHabitat.choices)
  type_operation = forms.CharField(required=False)
  anru = forms.BooleanField(required=False)
  nb_logement_non_conventionne = forms.IntegerField(required=False)
  nb_locaux_commerciaux = forms.IntegerField(required=False)
  nb_bureaux = forms.IntegerField(required=False)


class ProgrammmeCadastralForm(forms.Form):

  permis_construire = forms.CharField(required=False)
  date_acte_notarie = forms.DateField(required=False)
  date_achevement_previsible = forms.DateField(required=False)
  date_achat = forms.DateField(required=False)
  date_achevement = forms.DateField(required=False)
  vendeur = forms.CharField(required=True, max_length=5000, error_messages={
    'required': "Les informations relatives au vendeur sont obligatoires",
    'max_length':"Le message ne doit pas excéder 5000 characters",
    })
  acquereur = forms.CharField(required=True, max_length=5000, error_messages={
    'required': "Les informations relatives à l'aquéreur sont obligatoires",
    'max_length':"Le message ne doit pas excéder 5000 characters",
    })
  reference_notaire = forms.CharField(required=False, max_length=5000, error_messages={
    'max_length':"Le message ne doit pas excéder 5000 characters",
    })
  reference_publication_acte = forms.CharField(required=False, max_length=5000, error_messages={
    'max_length':"Le message ne doit pas excéder 5000 characters",
    })
