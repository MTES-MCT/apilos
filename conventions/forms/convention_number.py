from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from conventions.models.convention import Convention


class ConventionNumberForm(forms.Form):
    convention = None
    convention_numero = forms.CharField(
        max_length=250,
        label="Numéro de convention",
        help_text=mark_safe(
            "Le format de numéro de convention est standardisé, pour en savoir plus,"
            + ' consulter <a class="fr-link fr-text--xs"'
            + ' href="//docs.apilos.beta.gouv.fr/apres-la-validation-de-la-convention/'
            + 'instructeurs-parametres/numeration-convention"'
            + ' data-turbo="false" target="blank">notre FAQ</a>'
        ),
        error_messages={
            "max_length": (
                "La longueur totale du numéro de convention ne peut pas excéder"
                + " 250 caractères"
            ),
            "required": "Le numéro de convention est obligatoire",
        },
    )

    def clean_convention_numero(self):
        convention_numero = self.cleaned_data.get("convention_numero", 0)
        if (
            not self.convention.is_avenant()
            and Convention.objects.filter(numero=convention_numero)
            .exclude(pk=self.convention.pk)
            .exists()
        ):
            raise ValidationError(
                f"La convention de numero {convention_numero} existe déjà,"
                + " merci de choisir un autre numéro de convention."
            )
        return convention_numero
