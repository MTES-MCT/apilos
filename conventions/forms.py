from django import forms
from django.core.exceptions import ValidationError

from programmes.models import Lot

class ProgrammeSelectionForm(forms.Form):
  lot_uuid = forms.CharField(error_messages={'required': 'La selection du programme et de son financement est obligatoire'})

  def clean_lot_uuid(self):
    lot_uuid = self.cleaned_data['lot_uuid']

    print(lot_uuid)
    # check that lot_id exist in DB
    if not Lot.objects.get(uuid=lot_uuid):
      raise ValidationError("le programme avec ce financement n'existe pas")

    return lot_uuid
