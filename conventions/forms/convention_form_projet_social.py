from django import forms

from conventions.models.projet_social import ProjetSocial


class ProjetSocialForm(forms.ModelForm):
    publics_accueillis = forms.CharField(
        label=(
            "Préciser, parmi les personnes ayant des difficultés particulières d'accès au logement au sens de"
            " l'article 1er de la loi n° 90-449 du 31 mai 1990, les personnes ou familles qui seront accueillies"
            " dans la résidence sociale objet de la présente convention ainsi que les situations particulières"
            " auxquelles la résidence a vocation à répondre"
        ),
        widget=forms.Textarea,
    )
    actions_relogement_social = forms.CharField(
        label=(
            "Préciser si des actions spécifiques sont prévues pour le relogement et l'accompagnement social,"
            " notamment si la résidence sociale a pour vocation d'accueillir les populations prioritaires au sens"
            " de l'article 4 de la loi du 31 mai 1990"
        ),
        widget=forms.Textarea,
    )
    conditions_specifiques_accueil = forms.CharField(
        label="Conditions spécifiques d'accueil (s'il y a lieu)",
        widget=forms.Textarea,
        required=False,
    )
    conditions_admission = forms.CharField(
        label="Conditions d'admission dans la résidence sociale",
        widget=forms.Textarea,
    )
    duree_maximale_accueil_mois = forms.IntegerField(
        label="Durée maximale de l'accueil (en mois)",
        min_value=0,
        max_value=99
    )
    conditions_renouvellement_accueil = forms.CharField(
        label="Conditions de renouvellement de l'accueil",
        widget=forms.Textarea,
    )
    modalites_attribution = forms.CharField(
        label=(
            "Modalités d'attribution (organisme ou instance désignataire, "
            "type de public, conditions d'accès)"
        ),
        widget=forms.Textarea,
    )
    actions_caractere_social = forms.CharField(
        label="Actions à caractère social",
        widget=forms.Textarea,
    )
    action_insertion_par_logement = forms.CharField(
        label="Action spécifique pour l'insertion par le logement",
        widget=forms.Textarea,
    )
    projet_relogement = forms.CharField(
        label="Projet de relogement (s'il y a lieu)",
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, convention, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.convention = convention

    class Meta:
        model = ProjetSocial
        fields = (
            "publics_accueillis",
            "actions_relogement_social",
            "conditions_specifiques_accueil",
            "conditions_admission",
            "duree_maximale_accueil_mois",
            "conditions_renouvellement_accueil",
            "modalites_attribution",
            "actions_caractere_social",
            "action_insertion_par_logement",
            "projet_relogement",
        )
