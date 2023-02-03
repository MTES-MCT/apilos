"""
Étape Attribution du formulaire par étape de la convention (type Foyer et Résidence)
"""

from django import forms


class ConventionAttributionForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
    )
    attribution_reservation_prefectorale = forms.IntegerField(
        label="Part de réservations préfectorales",
        help_text="La part des locaux à usage privatif réservés par le préfet en pourcentage",
        error_messages={
            "required": "La part de réservations préfectoriales est obligatoire"
        },
    )

    attribution_modalites_reservations = forms.CharField(
        label="Modalités de gestion des reservations",
        error_messages={
            "required": "Les modalités de gestion des reservations sont obligatoires"
        },
    )

    attribution_modalites_choix_personnes = forms.CharField(
        label="Modalités de choix des personnes accueillies",
        error_messages={
            "required": "Les modalités de choix des personnes accueillies sont obligatoires"
        },
    )

    attribution_prestations_integrees = forms.CharField(
        required=False,
        label="Prestation intégrées dans la redevance (Liste)",
        help_text="Les prestations obligatoirement intégrées dans la redevance et non"
        + " prises en compte pour le calcul de l'APL (non prises en compte au titre des"
        + " charges récupérables)",
    )

    attribution_prestations_facultatives = forms.CharField(
        required=False,
        label="Prestations facultatives (Liste)",
        help_text="Prestations facultatives à la demande du résident facturées séparément",
    )


class ConventionResidenceAttributionForm(ConventionAttributionForm):

    attribution_residence_sociale_ordinaire = forms.BooleanField(
        required=False,
        label="Résidence sociale ordinaire",
        help_text="accueil de jeunes travailleurs ; de travailleurs migrants ; de personnes"
        + " éprouvant des difficultés sociale et économique particulières au sens de"
        + " l'article 1er de la loi n° 90-449 du 31 mai 1990 visant à la mise en œuvre"
        + " du droit au logement ainsi que les étudiants en situation de rupture sociale"
        + " et familiale qui peuvent, à titre exceptionnel, avoir accès à un nombre de"
        + " places très minoritaires",
    )
    attribution_pension_de_famille = forms.BooleanField(
        required=False,
        label="Pension de famille",
        help_text="accueil sans condition de durée de personnes dont la situation sociale"
        + " et psychologique ne permet pas leur accès à un logement ordinaire",
    )
    attribution_residence_accueil = forms.BooleanField(
        required=False,
        label="Résidence accueil",
        help_text="pension de famille pour personnes présentant un handicap psychique",
    )


class ConventionFoyerAttributionForm(ConventionAttributionForm):

    attribution_type = forms.ChoiceField(
        choices=[
            ("handicapees", "handicapees"),
            ("agees", "agees"),
            ("inclusif", "inclusif"),
        ]
    )
    # Foyer pour personnes handicapées
    attribution_agees_autonomie = forms.BooleanField(
        required=False,
        label="Résidence autonomie",
    )
    attribution_agees_ephad = forms.BooleanField(
        required=False,
        label="Établissement hébergeant des personnes âgées dépendantes (EHPAD)",
    )
    attribution_agees_desorientees = forms.BooleanField(
        required=False,
        label="Unité pour personnes désorientées (unités Alzheimer, ...)",
    )
    attribution_agees_petite_unite = forms.BooleanField(
        required=False,
        label="Petite unité de vie (établissement de moins de 25 places autorisées)",
    )
    attribution_agees_autre = forms.BooleanField(
        required=False,
        label="Autres [préciser]",
    )
    attribution_agees_autre_detail = forms.CharField(
        required=False,
        label="",
    )

    # Foyer pour personnes handicapées
    attribution_handicapes_foyer = forms.BooleanField(
        required=False,
        label="Foyer",
    )
    attribution_handicapes_foyer_de_vie = forms.BooleanField(
        required=False,
        label="Foyer de vie ou occupationnel",
    )
    attribution_handicapes_foyer_medicalise = forms.BooleanField(
        required=False,
        label="Foyer d'accueil médicalisé",
    )
    attribution_handicapes_autre = forms.BooleanField(
        required=False,
        label="Autres [préciser]",
    )
    attribution_handicapes_autre_detail = forms.CharField(
        required=False,
        label="",
    )
    attribution_inclusif_conditions_specifiques = forms.CharField(
        required=False,
        label="Conditions spécifiques d'accueil",
    )
    attribution_inclusif_conditions_admission = forms.CharField(
        required=False,
        label="Conditions d'admission dans l’habitat inclusif",
    )
    attribution_inclusif_modalites_attribution = forms.CharField(
        required=False,
        label="Modalités d'attribution",
    )
    attribution_inclusif_partenariats = forms.CharField(
        required=False,
        label="Partenariats concourant à la mise en œuvre du projet de vie sociale"
        + " et partagée mis en place",
    )
    attribution_inclusif_activites = forms.CharField(
        required=False,
        label="Activités proposées à l’ensemble des résidents dans le cadre du projet"
        + " de vie sociale et partagée",
    )

    def clean(self):
        cleaned_data = super().clean()
        attribution_type = cleaned_data.get("attribution_type")

        if attribution_type == "inclusif":
            for inclusif_required_field in [
                "attribution_inclusif_conditions_specifiques",
                "attribution_inclusif_conditions_admission",
                "attribution_inclusif_modalites_attribution",
                "attribution_inclusif_partenariats",
                "attribution_inclusif_activites",
            ]:
                clean_field = cleaned_data.get(inclusif_required_field)
                if not clean_field:
                    self.add_error(
                        inclusif_required_field,
                        "Ce champ est requis lors qu'il s'agit d'un habitat inclusif",
                    )

        if cleaned_data.get("attribution_agees_autre") and not cleaned_data.get(
            "attribution_agees_autre_detail"
        ):
            self.add_error(
                "attribution_agees_autre_detail",
                "Merci de préciser le type d'établissement retenu",
            )
        if cleaned_data.get("attribution_handicapes_autre") and not cleaned_data.get(
            "attribution_handicapes_autre_detail"
        ):
            self.add_error(
                "attribution_handicapes_autre_detail",
                "Merci de préciser le type d'établissement retenu",
            )
