from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from conventions.services.add_from_operation import (
    ConventionAddService,
    Operation,
    SelectOperationService,
)
from core.tests.test_utils import PGTrgmTestMixin
from programmes.models import NatureLogement
from programmes.tests.factories import ProgrammeFactory
from users.tests.factories import UserFactory


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class TestSelectOperationService(PGTrgmTestMixin, ParametrizedTestCase, TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.request.user = UserFactory(cerbere=True, is_superuser=True)
        self.request.session = {"habilitation_id": 5}

        ProgrammeFactory(
            uuid="67062edc-3ee8-4262-965f-98f885d418f4",
            numero_galion="2017DD01100057",
            nom="Programme 1",
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            ville="Bayonne",
            bailleur__nom="Bailleur A",
        )
        ProgrammeFactory(
            uuid="7fb89bd6-62f8-4c06-b15a-4fc81bc02995",
            numero_galion="2017DD01201254",
            nom="Programme 3",
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            ville="L'Isle-sur-la-Sorgue",
            bailleur__nom="Bailleur B",
        )

    @parametrize(
        "numero_operation, expected_matching, expected_operations",
        [
            param(
                "20220600006",
                True,
                [
                    Operation(
                        numero="20220600006",
                        nom="Programme 2",
                        bailleur="13055",
                        nature="LOO",
                        commune="Marseille",
                    )
                ],
                id="siap_match_exact",
            ),
            param(
                "2017DD01100057",
                True,
                [
                    Operation(
                        numero="2017DD01100057",
                        nom="Programme 1",
                        bailleur="Bailleur A",
                        nature="Logements ordinaires",
                        commune="Bayonne",
                    )
                ],
                id="apilos_match_exact",
            ),
            param(
                "2017DD01",
                False,
                [
                    Operation(
                        numero="2017DD01201254",
                        nom="Programme 3",
                        bailleur="Bailleur B",
                        nature="Résidence sociale",
                        commune="L'Isle-sur-la-Sorgue",
                    ),
                    Operation(
                        numero="2017DD01100057",
                        nom="Programme 1",
                        bailleur="Bailleur A",
                        nature="Logements ordinaires",
                        commune="Bayonne",
                    ),
                ],
                id="apilos_search_trgrm",
            ),
        ],
    )
    def test_fetch_operations(
        self, numero_operation, expected_matching, expected_operations
    ):
        service = SelectOperationService(
            request=self.request, numero_operation=numero_operation
        )
        exact_match, operations = service.fetch_operations()
        assert exact_match == expected_matching
        assert operations == expected_operations


class TestConventionAddService(TestCase):
    def basic_test(self):
        service = ConventionAddService(request=RequestFactory())
        assert service.get_form() is not None
