from django import forms
from django.core.exceptions import ValidationError

class BailleurForm(forms.Form):

  nom = forms.CharField(error_messages={'required': 'Le nom du bailleur est obligatoire'})
  siret = forms.CharField(max_length=14, error_messages={'required': 'Le SIRET du bailleur est obligatoire'})
  capital_social = forms.CharField(max_length=255, error_messages={'required': 'Le Capital social du bailleur est obligatoire'})
  adresse = forms.CharField(max_length=255, error_messages={'required': 'Le SIRET du bailleur est obligatoire'})
  code_postal = forms.CharField(max_length=255, error_messages={'required': 'Le SIRET du bailleur est obligatoire'})
  ville = forms.CharField(max_length=255, error_messages={'required': 'Le SIRET du bailleur est obligatoire'})
  dg_nom = forms.CharField(max_length=255, error_messages={'required': 'Le SIRET du bailleur est obligatoire'})
  dg_fonction = forms.CharField(max_length=255, error_messages={'required': 'Le SIRET du bailleur est obligatoire'})
  dg_date_deliberation = forms.DateField(error_messages={'required': 'Le SIRET du bailleur est obligatoire'})

  def clean_nom(self):
    nom = self.cleaned_data['nom']
    return nom
