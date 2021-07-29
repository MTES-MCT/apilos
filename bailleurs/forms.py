from django import forms
from django.core.exceptions import ValidationError

class BailleurForm(forms.Form):

  nom = forms.CharField(required=True, error_messages={
    'required': 'Le nom du bailleur est obligatoire',
    'max_length':"Le nom du bailleur ne doit pas excéder 255 caractères",
    })
  siret = forms.CharField(max_length=14, min_length=9, error_messages={
    'required': 'Le SIRET ou SIREN du bailleur est obligatoire',
    'max_length':'Le SIRET ou SIREN ne doivent pas excéder 14 caractères',
    'min_length':'Le SIRET ou SIREN doivent avoir 9 caractères minimum',
  })
  capital_social = forms.CharField(max_length=255, error_messages={
    'max_length':"Le capital social ne doit pas excéder 255 caractères",
  })
  adresse = forms.CharField(max_length=255, error_messages={
    'required': "L'adresse est obligatoire",
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
  dg_nom = forms.CharField(max_length=255, error_messages={
    'required': "Le nom du directeur général est obligatoire",
    'max_length':"Le nom du directeur général ne doit pas excéder 255 caractères",
  })
  dg_fonction = forms.CharField(max_length=255, error_messages={
    'required': "La fonction du directeur général est obligatoire",
    'max_length':"La fonction du directeur général ne doit pas excéder 255 caractères",
  })
  dg_date_deliberation = forms.DateField(error_messages={
    'required': "La date de délibération est obligatoire",
  })

  def clean_nom(self):
    nom = self.cleaned_data['nom']
    return nom
