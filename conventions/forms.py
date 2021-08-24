from django import forms
from django.core.exceptions import ValidationError

class ConventionCommentForm(forms.Form):

  comments = forms.CharField(required=False, max_length=5000, error_messages={
    'max_length':"Le message ne doit pas excéder 5000 characters",
    })

class ConventionFinancementForm(forms.Form):

  date_fin_conventionnement = forms.DateField(required=False)
