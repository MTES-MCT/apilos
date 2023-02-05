from django import forms
from conventions.forms.convention_form_bailleur import ConventionBailleurForm


class BailleurForm(ConventionBailleurForm):
    def __init__(self, *args, bailleurs=None, **kwargs) -> None:
        if bailleurs:
            self.declared_fields["bailleur"].choices = bailleurs
        super().__init__(*args, **kwargs)

    bailleur = forms.ChoiceField(
        required=False,
        label="Bailleur parent",
        help_text="Les utilisateurs du bailleur parent à les mêmes droits sur ce bailleur",
        initial=None,
        choices=[],
    )
