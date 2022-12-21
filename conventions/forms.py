import datetime
from dateutil.relativedelta import relativedelta

from django import forms
from django.forms import BaseFormSet, formset_factory
from django.forms.fields import FileField
from django.core.exceptions import ValidationError

from programmes.models import (
    Financement,
    TypeOperation,
)
from conventions.models import ConventionType1and2, Preteur, AvenantType


class ConventionFoyerVariantesForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
    )
    foyer_variante_1 = forms.BooleanField(
        required=False,
        label="Variante 1",
        help_text="programme existant dont la construction a été financée dans les"
        + " conditions du 1° de l'article R. 832-21 du code de la construction et de"
        + " l'habitation",
    )
    foyer_variante_2 = forms.BooleanField(
        required=False,
        label="Variante 2",
        help_text="programme existant dont l'amélioration ou l'acquisition suivie d'une"
        + " amélioration est financée dans les conditions prévues au 2° de l'article"
        + " R. 832-21 du code de la construction et de l'habitation",
    )
    foyer_variante_2_travaux = forms.CharField(
        max_length=5000,
        required=False,
        label="Description du programme des travaux ",
        help_text="A renseigner pour une Acquisition/Amélioration, conformément à"
        + " l’article 14 de la convention",
    )
    foyer_variante_3 = forms.BooleanField(
        required=False,
        label="Variante 3",
        help_text="programme neuf dont la construction est financée dans les conditions"
        + " visées au 3° de l'article R. 832-21 du code de la construction et de"
        + " l'habitation",
    )

    def clean(self):
        cleaned_data = super().clean()

        if (
            not cleaned_data.get("foyer_variante_1")
            and not cleaned_data.get("foyer_variante_2")
            and not cleaned_data.get("foyer_variante_3")
        ):
            self.add_error(None, "Au moins 1 variante doit-être sélectionnée")
        if cleaned_data.get("foyer_variante_2") and not cleaned_data.get(
            "foyer_variante_2_travaux"
        ):
            self.add_error(
                "foyer_variante_2_travaux",
                "Si la Variante 2 est sélectionnée, vous devez décrire le programme des"
                + " travaux",
            )


class ConventionFoyerAttributionForm(forms.Form):

    uuid = forms.UUIDField(
        required=False,
    )
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
    attribution_reservation_prefectoral = forms.IntegerField(
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


class ConventionCommentForm(forms.Form):

    uuid = forms.UUIDField(
        required=False,
        label="Commentaires",
    )

    attached = forms.CharField(
        required=False,
        label="Fichiers à joindre à la convention",
        help_text="Téléversez ici les fichiers à joindre à votre convention le cas"
        + " echéant et si nécessaire, par exemple"
        + " \r\n  • Autorisation délivrée au gestionnaire par le président du conseil"
        + " départemental ou par l'autorité compétente de l'état dans le cadre d'un"
        + " foyer hors habitat inclusif"
        + " \r\n  • Convention de location"
        + " \r\n  • Programme et des travaux"
        + " \r\n  • Échéancier du programme des travaux"
        + " \r\n  • …",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    attached_files = forms.CharField(
        required=False,
    )

    comments = forms.CharField(
        required=False,
        label="Ajoutez vos commentaires à l'attention de l'instructeur",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )

    comments_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )


class ConventionFinancementForm(forms.Form):

    prets = []
    convention = None

    uuid = forms.UUIDField(
        required=False,
        label="Prêts et financements",
    )
    annee_fin_conventionnement = forms.TypedChoiceField(
        required=True,
        label="",
        coerce=int,
        choices=[(str(year), str(year)) for year in range(2021, 2121)],
        error_messages={
            "required": "La date de fin de conventionnement est obligatoire",
        },
    )
    fond_propre = forms.FloatField(
        required=False,
        label="Fonds propres",
    )
    historique_financement_public = forms.CharField(
        required=False,
        label="Historique de financement public",
        max_length=5000,
        error_messages={
            "max_length": "L'historique de financement public ne doit pas excéder 5000 caractères",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        annee_fin_conventionnement = cleaned_data.get("annee_fin_conventionnement")

        if (
            self.prets
            and self.convention is not None
            and annee_fin_conventionnement is not None
        ):
            if self.convention.financement == Financement.PLS:
                self._pls_end_date_validation(annee_fin_conventionnement)
            elif self.convention.programme.type_operation == TypeOperation.SANSTRAVAUX:
                self._sans_travaux_end_date_validation(annee_fin_conventionnement)
            else:
                self._other_end_date_validation(annee_fin_conventionnement)

    def _pls_end_date_validation(self, annee_fin_conventionnement):
        today = datetime.date.today()

        min_years = today.year + 15
        max_years = today.year + 40
        if today.month > 6:
            min_years = min_years + 1
            max_years = max_years + 1
        if annee_fin_conventionnement < min_years:
            self.add_error(
                "annee_fin_conventionnement",
                (
                    "L'année de fin de conventionnement ne peut être inférieur à "
                    + f"{min_years}"
                ),
            )
        if annee_fin_conventionnement > max_years:
            self.add_error(
                "annee_fin_conventionnement",
                (
                    "L'année de fin de conventionnement ne peut être supérieur à "
                    + f"{max_years}"
                ),
            )

    def _sans_travaux_end_date_validation(self, annee_fin_conventionnement):
        today = datetime.date.today()

        min_years = today.year + 9
        if today.month > 6:
            min_years = min_years + 1
        if annee_fin_conventionnement < min_years:
            self.add_error(
                "annee_fin_conventionnement",
                (
                    "L'année de fin de conventionnement ne peut être inférieur à "
                    + f"{min_years}"
                ),
            )

    def _other_end_date_validation(self, annee_fin_conventionnement):
        end_conv = None
        cdc_pret = None
        for pret in self.prets:
            if pret.cleaned_data["preteur"] in ["CDCF", "CDCL"]:
                if pret.cleaned_data["date_octroi"] and pret.cleaned_data["duree"]:
                    end_datetime = pret.cleaned_data["date_octroi"] + relativedelta(
                        years=int(pret.cleaned_data["duree"])
                    )
                    if not end_conv or end_datetime > end_conv:
                        end_conv = end_datetime
                        cdc_pret = pret
        if end_conv and cdc_pret:
            cdc_end_year = end_conv.year
            if end_conv.year - cdc_pret.cleaned_data["date_octroi"].year < 9:
                cdc_end_year = cdc_pret.cleaned_data["date_octroi"].year + 9
            # don't add a year for FOYER because end of convention is the 31/12
            if (
                not self.convention.programme.is_foyer()
                and end_conv
                and end_conv.month > 6
            ):
                cdc_end_year = cdc_end_year + 1
            if annee_fin_conventionnement < cdc_end_year:
                self.add_error(
                    "annee_fin_conventionnement",
                    (
                        "L'année de fin de conventionnement ne peut être inférieur à "
                        + f"{cdc_end_year}"
                    ),
                )


class PretForm(forms.Form):

    uuid = forms.UUIDField(
        required=False,
        label="Prêt ou financement",
    )
    numero = forms.CharField(
        required=False,
        label="",
        max_length=255,
        error_messages={
            "max_length": "Le numero ne doit pas excéder 255 caractères",
        },
    )
    preteur = forms.TypedChoiceField(required=False, label="", choices=Preteur.choices)
    autre = forms.CharField(
        required=False,
        label="",
        max_length=255,
        error_messages={
            "max_length": "Le prêteur ne doit pas excéder 255 caractères",
        },
    )
    date_octroi = forms.DateField(
        required=False,
        label="",
    )
    duree = forms.IntegerField(
        required=False,
        label="",
    )
    montant = forms.DecimalField(
        label="",
        max_digits=12,
        decimal_places=2,
        error_messages={
            "required": "Le montant du prêt est obligatoire",
            "max_digits": "Le montant du prêt doit-être inférieur à 10 000 000 000 €",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        preteur = cleaned_data.get("preteur")

        if preteur in ["CDCF", "CDCL"]:
            if not cleaned_data.get("date_octroi"):
                self.add_error(
                    "date_octroi",
                    "La date d'octroi est obligatoire pour un prêt de la "
                    + "Caisse de dépôts et consignations",
                )
            if not cleaned_data.get("duree"):
                self.add_error(
                    "duree",
                    "La durée est obligatoire pour un prêt de la Caisse de dépôts et consignations",
                )
            if not cleaned_data.get("numero"):
                self.add_error(
                    "numero",
                    (
                        "Le numéro est obligatoire pour un prêt"
                        + " de la Caisse de dépôts et consignations"
                    ),
                )
        if preteur in ["AUTRE"]:
            if not cleaned_data.get("autre"):
                self.add_error("autre", "Merci de préciser le prêteur")


class BasePretFormSet(BaseFormSet):

    convention = None

    def clean(self):
        self.manage_cdc_validation()

    def manage_cdc_validation(self):
        if (
            self.convention is not None
            and self.convention.financement != Financement.PLS
            and self.convention.programme.type_operation != TypeOperation.SANSTRAVAUX
        ):
            for form in self.forms:
                if form.cleaned_data.get("preteur") in ["CDCF", "CDCL"]:
                    return
            error = ValidationError(
                "Au moins un prêt à la Caisee des dépôts et consignations doit-être déclaré "
                + "(CDC foncière, CDC locative)"
            )
            self._non_form_errors.append(error)


PretFormSet = formset_factory(PretForm, formset=BasePretFormSet, extra=0)


class UploadForm(forms.Form):

    file = FileField(
        error_messages={
            "required": (
                "Vous devez sélectionner un fichier avant "
                + "de cliquer sur le bouton 'Téléverser'"
            ),
        }
    )


class NotificationForm(forms.Form):

    send_copy = forms.BooleanField(required=False)
    from_instructeur = forms.BooleanField(required=False)
    all_bailleur_users = forms.BooleanField(required=False, initial=False)
    comment = forms.CharField(
        required=False,
        label="Ajouter un commentaire à l'attention du bailleur (optionnel)",
        max_length=5000,
        error_messages={
            "max_length": "Le commentaire ne doit pas excéder 5000 caractères",
        },
    )


class ConventionNumberForm(forms.Form):
    convention = None
    convention_numero = forms.CharField(
        max_length=250,
        label="Numéro de convention",
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
        if convention_numero == self.convention.get_convention_prefix():
            raise ValidationError(
                "Attention, le champ est uniquement prérempli avec le préfixe du numéro de "
                + "convention déterminé pour votre administration. Il semble que vous n'ayez pas "
                + "ajouté, à la suite de ce préfixe, de numéro d'ordre de la convention."
            )
        return convention_numero


class ConventionResiliationForm(forms.Form):

    date_resiliation = forms.DateField(
        required=True,
        label="Spécifier la date de résiliation/dénonciation",
        error_messages={
            "required": "Vous devez saisir une date de résiliation",
        },
    )


class ConventionType1and2Form(forms.Form):

    uuid = forms.UUIDField(
        required=False,
        label="Convention de type I et II",
    )
    type1and2 = forms.TypedChoiceField(
        required=False,
        choices=ConventionType1and2.choices,
        label="Type de convention I ou II",
    )

    type2_lgts_concernes_option1 = forms.BooleanField(
        required=False,
        label=(
            "1° financés dans les conditions prévues par le chapitre Ier du titre Ier du livre III"
            + " du code de la construction et de l'habitation, par le titre II de la loi du 13"
            + " juillet 1928, ainsi que par l'article 269 du code de l'urbanisme et de"
            + " l'habitation, abrogé par le décret n° 63-1323 du 24 décembre 1963"
        ),
        help_text="ILM 28, LOGECO, logements construits à l'aide des anciens prêts du CFF",
    )
    type2_lgts_concernes_option2 = forms.BooleanField(
        required=False,
        label=(
            "2° définis au II de l'article D. 331-1 du code de la construction et de l'habitation"
            + " et construits, améliorés, acquis, acquis et améliorés par les maîtres d'ouvrage"
            + " mentionnés au 3° ou 4° de l'article D. 331-14 du même code"
        ),
        help_text=(
            "Logements appartenant aux collectivités territoriales ou aux organismes agréés"
            + " (3° et 4°de l'article R.331-14) et financés en PLA-I pour leur construction, leur"
            + " acquisition, ou leur acquisition-amélioration"
        ),
    )
    type2_lgts_concernes_option3 = forms.BooleanField(
        required=False,
        label=(
            "3° ayant bénéficié d'une décision favorable prise dans les conditions prévues aux"
            + " articles D. 331-3 et D. 331-6 du code de la construction et de l'habitation et"
            + " faisant l'objet de prêts mentionnés à la sous-section 3 de la section 1 du"
            + " chapitre unique du titre III du livre III du même code pour leur amélioration,"
            + " leur acquisition ou leur acquisition-amélioration"
        ),
        help_text=(
            "Logements financés en PLS pour leur acquisition ou leur"
            + " acquisition-amélioration",
        ),
    )
    type2_lgts_concernes_option4 = forms.BooleanField(
        required=False,
        label=(
            "4° donnant lieu pour leur amélioration à une subvention de l'Etat définie par les"
            + " articles D. 323-1 à D. 323-11 du code de la construction et de l'habitation"
        ),
        help_text="Logements améliorés à l'aide d'une PALULOS ou d'un PAM",
    )
    type2_lgts_concernes_option5 = forms.BooleanField(
        required=False,
        label=(
            "5° acquis et améliorés par les collectivités locales ou leurs groupements et"
            + " bénéficiant des subventions pour réaliser les opérations prévues au 4° de"
            + " l'article D. 331-14 précité"
        ),
        help_text=(
            "Logements financés en PLUS pour leur construction, leur acquisition ou leur"
            + " acquisition-amélioration par des collectivités locales ou leurs groupements"
        ),
    )
    type2_lgts_concernes_option6 = forms.BooleanField(
        required=False,
        label=(
            "6° appartenant aux bailleurs autres que les sociétés d'économie mixte et mentionnés au"
            + " quatrième alinéa de l'article 41 ter de la loi n° 86-1290 du 23 décembre 1986"
            + " tendant à favoriser l'investissement locatif, l'accession à la propriété de"
            + " logements sociaux et le développement de l'offre foncière"
        ),
        help_text=(
            "Logements conventionnés avec ou sans travaux appartenant aux sociétés immobilières"
            + " à participation majoritaire de la CDC, aux collectivités publiques, aux sociétés"
            + " filiales d'un organisme collecteur de la contribution des employeurs à l'effort"
            + " de construction et aux filiales de ces organismes"
        ),
    )
    type2_lgts_concernes_option7 = forms.BooleanField(
        required=False,
        label=(
            "7° appartenant à l'association foncière mentionnée à l'article L. 313-34 du code de la"
            + " construction et de l'habitation ou à l'une de ses filiales"
        ),
        help_text="Logements appartenant à l'association foncière logement",
    )
    type2_lgts_concernes_option8 = forms.BooleanField(
        required=False,
        label=(
            "8° satisfaisant aux conditions fixées par l'article L. 831-1 (2°) du code de la"
            + " construction et de l'habitation"
        ),
        help_text=(
            "Autres logements construits, acquis ou améliorés sans le concours financier"
            + " de l'Etat"
        ),
    )


class AvenantForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
    )

    avenant_type = forms.ChoiceField(
        label="Type d'avenant",
        choices=AvenantType.get_as_choices,
        required=True,
    )


class InitavenantsforavenantForm(forms.Form):
    uuid = forms.UUIDField(
        required=False,
    )


class AvenantsforavenantForm(forms.Form):

    avenant_types = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label="Type d'avenant",
        choices=AvenantType.get_as_choices,
        required=True,
    )
    error_messages = (
        {
            "required": "Vous devez saisir un ou plusieurs types d'avenant",
        },
    )
    desc_avenant = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Informations sur la nature de l'avenant.",
    )
    nom_fichier_signe = forms.FileField(
        required=False,
    )
