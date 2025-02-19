from datetime import date, timedelta

from django.test import TestCase
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from bailleurs.tests.factories import BailleurFactory
from conventions.models import ConventionStatut
from conventions.services.search import ConventionSearchService
from conventions.tests.factories import AvenantFactory, ConventionFactory
from core.tests.test_utils import PGTrgmTestMixin
from programmes.models.choices import Financement, NatureLogement
from programmes.tests.factories import ProgrammeFactory
from users.tests.factories import UserFactory


class TestUserConventionSearchService(PGTrgmTestMixin, ParametrizedTestCase, TestCase):
    def setUp(self) -> None:
        self.user = UserFactory(is_staff=True, is_superuser=True)

        ConventionFactory(
            uuid="fbb9890f-171b-402d-a35e-71e1bd791b70",
            numero="33N611709S70002-9",
            statut=ConventionStatut.SIGNEE.label,
            televersement_convention_signee_le="2024-01-01",
            programme=ProgrammeFactory(
                anru=True,
                numero_operation="2017DD01100057",
                nom="Le Clos de l'Ille - Rue de l'Occitanie - Séniors",
                ville="Bourg-en-Bresse",
                adresse="Pl. de l'Hôtel de ville",
                code_postal="01012",
                nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
                bailleur=BailleurFactory(
                    uuid="9eaece28-e15f-4d23-94f5-20902f5b0180",
                    nom="SEMCODAN Société d'Economie Mixte Courbevoie-Danto",
                    siret="34322777300011",
                ),
            ),
            create_lot=True,
            create_lot__financement=Financement.PLUS,
        )

        ConventionFactory(
            uuid="fbb9890f-171b-402d-a35e-71e1bd791b71",
            numero="51/2015/2006-569/049R",
            statut=ConventionStatut.PROJET.label,
            programme=ProgrammeFactory(
                anru=False,
                numero_operation="20230600400040",
                nom="ANTIBES 31 avenue de Nice",
                ville="Antibes",
                adresse="31 avenue de Nice",
                code_postal="06004",
                nature_logement=NatureLogement.RESIDENCEUNIVERSITAIRE,
                bailleur=BailleurFactory(
                    nom="VILOGIA SOCIETE ANONYME D'HLM",
                    siret="475 680 815 00051",
                ),
            ),
            create_lot=True,
            create_lot__financement=Financement.PLAI,
        )

        convention = ConventionFactory(
            uuid="fbb9890f-171b-402d-a35e-71e1bd791b72",
            numero="32O665408Y777889",
            statut=ConventionStatut.INSTRUCTION.label,
            programme=ProgrammeFactory(
                anru=True,
                numero_operation="2017490070049",
                nom="ANGERS - Les Eclateries - ilot D ",
                ville="Angers",
                adresse="Rue de la Chalouère",
                code_postal="49007",
                nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
                bailleur=BailleurFactory(
                    nom="PODELIHA",
                    siret="05720113900029",
                ),
            ),
            create_lot=True,
            create_lot__financement=Financement.PLS,
        )

        AvenantFactory(
            uuid="a6862260-5afa-4e2c-ae07-a39276c55e46",
            parent=convention,
            statut=ConventionStatut.ANNULEE.label,
            programme=convention.programme,
            create_lot=True,
            create_lot__financement=Financement.PLS,
        )

        programme = ProgrammeFactory(
            anru=False,
            numero_operation="2014E891109087",
            nom="blah blah blah",
            ville="Marseille",
            adresse="Rue de la canebière",
            code_postal="13000",
            nature_logement=NatureLogement.RESIDENCEUNIVERSITAIRE,
            bailleur=BailleurFactory(
                uuid="d9639714-87c5-4602-bb9d-a83dabdb304a",
                nom="bailleur 2",
                siret="123456789",
            ),
        )

        ConventionFactory(
            uuid="53702e67-60c1-431e-baa9-449960cf8bcb",
            numero="QHKINZYDKDLSNJW",
            statut=ConventionStatut.RESILIEE.label,
            televersement_convention_signee_le="2014-01-01",
            date_resiliation=date.today() + timedelta(days=1),
            programme=programme,
            create_lot=True,
            create_lot__financement=Financement.PALULOS,
        )

        ConventionFactory(
            uuid="4c337449-4fbc-42de-9f93-948a4dd65ee1",
            numero="QHKINZYDKDLSNJX",
            statut=ConventionStatut.RESILIEE.label,
            televersement_convention_signee_le="2014-01-01",
            date_resiliation=date.today() - timedelta(days=1),
            programme=programme,
            create_lot=True,
            create_lot__financement=Financement.PALULOS,
        )

        ConventionFactory(
            uuid="60511ac3-f979-4a13-917d-1c746b4e4390",
            numero="QHKINZYDKDLSNJY",
            statut=ConventionStatut.DENONCEE.label,
            televersement_convention_signee_le="2014-01-01",
            date_denonciation=date.today() + timedelta(days=1),
            programme=programme,
            create_lot=True,
            create_lot__financement=Financement.PALULOS,
        )

        ConventionFactory(
            uuid="75d19956-2561-4987-9dbf-497803e152f8",
            numero="QHKINZYDKDLSNJZ",
            statut=ConventionStatut.DENONCEE.label,
            televersement_convention_signee_le="2014-01-01",
            date_denonciation=date.today() - timedelta(days=1),
            programme=programme,
            create_lot=True,
            create_lot__financement=Financement.PALULOS,
        )

    @parametrize(
        "search_filters, expected",
        [
            param(
                {"anru": "on"},
                [
                    "fbb9890f-171b-402d-a35e-71e1bd791b72",
                    "fbb9890f-171b-402d-a35e-71e1bd791b70",
                    "a6862260-5afa-4e2c-ae07-a39276c55e46",
                ],
                id="anru",
            ),
            param(
                {"statuts": ConventionStatut.PROJET.label},
                ["fbb9890f-171b-402d-a35e-71e1bd791b71"],
                id="statuts_unique",
            ),
            param(
                {
                    "statuts": f"{ConventionStatut.PROJET.label},{ConventionStatut.INSTRUCTION.label}"
                },
                [
                    "fbb9890f-171b-402d-a35e-71e1bd791b72",
                    "fbb9890f-171b-402d-a35e-71e1bd791b71",
                ],
                id="statuts_multiples",
            ),
            param(
                {"financement": Financement.PLAI},
                ["fbb9890f-171b-402d-a35e-71e1bd791b71"],
                id="financement",
            ),
            param(
                {"nature_logement": NatureLogement.LOGEMENTSORDINAIRES},
                [
                    "fbb9890f-171b-402d-a35e-71e1bd791b72",
                    "fbb9890f-171b-402d-a35e-71e1bd791b70",
                    "a6862260-5afa-4e2c-ae07-a39276c55e46",
                ],
                id="nature_logement",
            ),
            param(
                {"date_signature": "2024"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="date_sgnature",
            ),
            param(
                {"bailleur": "9eaece28-e15f-4d23-94f5-20902f5b0180"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="bailleur",
            ),
            param(
                {"search_operation_nom": "rue occitanie"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="programme_nom",
            ),
            param(
                {"search_numero": "33N611709S700029"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="numero_convention_exact",
            ),
            # param(
            #     {"search_numero": "33N6117090002"},
            #     ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
            #     id="numero_convention_avec_erreurs",
            # ),
            param(
                {"search_numero": "51/2015/2006-569/049R"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b71"],
                id="numero_convention_avec_caracteres_speciaux",
            ),
            param(
                {"search_numero": "32O665408Y777889"},
                [
                    "fbb9890f-171b-402d-a35e-71e1bd791b72",
                    "a6862260-5afa-4e2c-ae07-a39276c55e46",
                ],
                id="numero_convention_avec_avenant",
            ),
            # param(
            #     {"search_numero": "20230600400430"},
            #     ["fbb9890f-171b-402d-a35e-71e1bd791b71"],
            #     id="numero_operation_avec_erreurs",
            # ),
            # param(
            #     {"search_numero": "51/2015/2006-569/049R 33N611709S700029"},
            #     [
            #         "fbb9890f-171b-402d-a35e-71e1bd791b71",
            #         "fbb9890f-171b-402d-a35e-71e1bd791b70",
            #     ],
            #     id="numero_operation_et_convention",
            # ),
            param(
                {"search_numero": "0029"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="numero_convention_4_derniers_caracteres",
            ),
            param(
                {"search_numero": "29"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="numero_convention_2_derniers_caracteres",
            ),
            param(
                {"search_numero": "9"},
                [
                    "fbb9890f-171b-402d-a35e-71e1bd791b72",
                    "fbb9890f-171b-402d-a35e-71e1bd791b70",
                ],
                id="numero_convention_dernier_caractere",
            ),
            param(
                {"search_lieu": "01012"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="programme_code_postal",
            ),
            param(
                {"search_lieu": "bourg-en-bresss 01012"},
                ["fbb9890f-171b-402d-a35e-71e1bd791b70"],
                id="programme_commune_et_code_postal",
            ),
            param(
                {"statuts": ConventionStatut.SIGNEE.label},
                [
                    "60511ac3-f979-4a13-917d-1c746b4e4390",
                    "53702e67-60c1-431e-baa9-449960cf8bcb",
                    "fbb9890f-171b-402d-a35e-71e1bd791b70",
                ],
                id="conv_en_resiliation",
            ),
        ],
    )
    def test_search_filters(self, search_filters: str, expected: list[str]):
        service = ConventionSearchService(user=self.user, search_filters=search_filters)
        self.assertEqual([str(c.uuid) for c in service.get_queryset()], expected)
