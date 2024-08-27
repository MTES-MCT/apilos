from django import forms

from apilos_settings.models import Departement


class DelegatairesForm(forms.Form):
    def __init__(self, *args, administrations, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.declared_fields["administration"].choices = administrations

    administration = forms.ChoiceField(
        label="Administration délégataire",
        choices=[],
        help_text="L’administration délégataire à laquelle les conventions seront attribuées",
        error_messages={
            "required": "L'administration est obligatoire",
        },
    )

    departement = forms.ModelChoiceField(
        label="Département",
        queryset=Departement.objects.all(),
        required=True,
        empty_label=None,
    )

    no_dry_run = forms.BooleanField(label="No dry run", required=False)
