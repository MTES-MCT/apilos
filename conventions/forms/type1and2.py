from django import forms

from conventions.models import ConventionType1and2


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
            " acquisition-amélioration"
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
