from django import forms


class ConventionFoyerVariantesForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
    )
    foyer_residence_variante_1 = forms.BooleanField(
        required=False,
        label="Variante 1",
        help_text="programme existant dont la construction a été financée dans les"
        + " conditions du 1° de l'article R. 832-21 du code de la construction et de"
        + " l'habitation",
    )
    foyer_residence_variante_2 = forms.BooleanField(
        required=False,
        label="Variante 2",
        help_text="programme existant dont l'amélioration ou l'acquisition suivie d'une"
        + " amélioration est financée dans les conditions prévues au 2° de l'article"
        + " R. 832-21 du code de la construction et de l'habitation",
    )
    foyer_residence_variante_2_travaux = forms.CharField(
        max_length=5000,
        required=False,
        label="Description du programme des travaux ",
        help_text="A renseigner pour une Acquisition/Amélioration, conformément à"
        + " l’article 14 de la convention",
    )
    foyer_residence_variante_3 = forms.BooleanField(
        required=False,
        label="Variante 3",
        help_text="programme neuf dont la construction est financée dans les conditions"
        + " visées au 3° de l'article R. 832-21 du code de la construction et de"
        + " l'habitation",
    )

    def clean(self):
        cleaned_data = super().clean()

        if (
            not cleaned_data.get("foyer_residence_variante_1")
            and not cleaned_data.get("foyer_residence_variante_2")
            and not cleaned_data.get("foyer_residence_variante_3")
        ):
            self.add_error(None, "Au moins 1 variante doit-être sélectionnée")
        if cleaned_data.get("foyer_residence_variante_2") and not cleaned_data.get(
            "foyer_residence_variante_2_travaux"
        ):
            self.add_error(
                "foyer_residence_variante_2_travaux",
                "Si la Variante 2 est sélectionnée, vous devez décrire le programme des"
                + " travaux",
            )
