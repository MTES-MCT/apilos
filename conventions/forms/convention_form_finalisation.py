from django import forms
from django.utils.safestring import mark_safe

from conventions.models.convention import Convention


class FinalisationNumeroForm(forms.Form):
    convention: Convention
    uuid = forms.UUIDField(
        required=False,
        label="Finalisation numéro",
    )
    numero = forms.CharField(
        label="Numéro de convention",
        help_text=mark_safe(
            "Cet identifiant proposé est unique et standardisé à l'échelle nationale."
            '<a href="https://siap-logement.atlassian.net/wiki/x/f4Bu">En savoir plus</a>'
        ),
        max_length=255,
        min_length=1,
        required=True,
        error_messages={
            "required": "Le numéro de la convention est obligatoire",
            "min_length": "Le numéro de la convention est obligatoire",
            "max_length": "Le numéro de la convention ne doit pas excéder 255 caractères",
        },
    )

    def __init__(self, *args, convention: Convention, **kwargs):
        self.convention = convention
        super().__init__(*args, **kwargs)

    def clean_numero(self):
        numero = self.cleaned_data["numero"]
        if (
            not self.convention.is_avenant()
            and Convention.objects.filter(numero=numero)
            .exclude(pk=self.convention.pk)
            .exists()
        ):
            raise forms.ValidationError(
                f"La convention de numero {numero} existe déjà,"
                + " merci de choisir un autre numéro de convention."
            )
        return numero


class FinalisationCerfaForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
        label="Finalisation cerfa",
    )
    fichier_override_cerfa = forms.CharField(required=False, label="Cerfa personalisé")
    fichier_override_cerfa_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type docx sont acceptés dans la limite de 100 Mo",
    )
