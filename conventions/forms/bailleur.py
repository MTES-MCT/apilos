from django import forms
from django.db.models import QuerySet

from bailleurs.models import Bailleur
from conventions.forms.convention_form_bailleur import ConventionBailleurForm


class BailleurForm(ConventionBailleurForm):
    bailleur = forms.ModelChoiceField(
        required=False,
        label="Bailleur parent",
        help_text="Les utilisateurs du bailleur parent à les mêmes droits sur ce bailleur",
        initial=None,
        queryset=Bailleur.objects.none(),
        to_field_name="uuid",
    )

    def __init__(self, *args, bailleur_query: QuerySet, **kwargs) -> None:
        self.declared_fields["bailleur"].queryset = bailleur_query
        print(self.declared_fields["bailleur"].queryset)

        super().__init__(*args, **kwargs)
