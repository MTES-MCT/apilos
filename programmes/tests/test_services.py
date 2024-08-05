from datetime import date
from unittest.mock import patch

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from apilos_settings.models import Departement
from conventions.tests.factories import ConventionFactory
from programmes.models import IndiceEvolutionLoyer, NatureLogement
from programmes.services import LoyerRedevanceUpdateComputer, OperationService
from programmes.tests.factories import DepartementFactory, ProgrammeFactory
from siap.siap_client.client import SIAPClient
from users.tests.factories import UserFactory


@pytest.fixture
def operation_seconde_vie():
    return {
        "donneesOperation": {
            "aides": [{"code": "SECD_VIE", "libelle": "Seconde vie"}],
        },
        "detailsOperation": [
            {
                "aide": {"code": "PLUS", "libelle": "PLUS"},
            },
            {
                "aide": {"code": "PLAI", "libelle": "PLAI"},
            },
        ],
    }


@pytest.fixture
def operation_service(operation_seconde_vie):
    factory = RequestFactory()
    request = factory.get("/settings/administrations/")
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session["habilitation_id"] = "1"
    request.session.save()
    user = UserFactory(is_superuser=True)
    request.user = user
    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation_seconde_vie
        return OperationService(request=request, numero_operation="20220600016")


@pytest.mark.django_db
class TestOperationService:
    def test_init(self, operation_seconde_vie, operation_service):
        assert operation_service.numero_operation == "20220600016"
        assert operation_service.operation == operation_seconde_vie

    @pytest.mark.parametrize(
        "aides,expected",
        [
            ({"code": "SECD_VIE", "libelle": "Seconde vie"}, True),
            ({"code": "PLUS", "libelle": "PLUS"}, False),
        ],
    )
    def test_is_seconde_vie(self, operation_service, aides, expected):
        operation_service.operation = {
            "donneesOperation": {
                "numeroOperation": "20220600016",
                "aides": [aides],
            },
        }
        assert operation_service.is_seconde_vie() == expected

    def test_has_conventions(self, operation_service):
        operation_service.programme = ProgrammeFactory()
        assert not operation_service.has_conventions()

        ConventionFactory.create_batch(2, lot__programme=operation_service.programme)
        assert operation_service.has_conventions()


class LoyerRedevanceUpdateComputerTest(TestCase):
    def setUp(self):
        self.departement = Departement.objects.get_or_create(
            code_insee="10", nom="Aube"
        )[0]

    @classmethod
    def setUpTestData(cls):
        departement1 = DepartementFactory(code_insee="2A", nom="Corse-du-Sud")
        departement2 = DepartementFactory(code_insee="2B", nom="Haute-Corse")
        data = [
            {
                "annee": 2023,
                "evolution": 2,
                "date_debut": "2022-01-01",
                "date_fin": "2022-12-31",
                "departements": [departement1, departement2],
            },
            {
                "annee": 2023,
                "evolution": 3.6,
                "date_debut": "2022-01-01",
                "date_fin": "2022-12-31",
                "departements": None,
            },
            {
                "annee": 2022,
                "evolution": 0.42,
                "date_debut": "2021-01-01",
                "date_fin": "2021-12-31",
            },
            {
                "annee": 2021,
                "evolution": 0.66,
                "date_debut": "2020-01-01",
                "date_fin": "2020-12-31",
            },
            {
                "annee": 2020,
                "evolution": 1.53,
                "date_debut": "2019-01-01",
                "date_fin": "2019-12-31",
            },
            {
                "annee": 2019,
                "evolution": 1.25,
                "date_debut": "2018-01-01",
                "date_fin": "2018-12-31",
            },
            {
                "annee": 2018,
                "evolution": 0,
                "date_debut": "2017-01-01",
                "date_fin": "2017-12-31",
            },
            {
                "annee": 2017,
                "evolution": 0,
                "date_debut": "2016-01-01",
                "date_fin": "2016-12-31",
            },
            {
                "annee": 2016,
                "evolution": 0.08,
                "date_debut": "2015-01-01",
                "date_fin": "2015-12-31",
            },
            {
                "annee": 2015,
                "evolution": 0.57,
                "date_debut": "2014-01-01",
                "date_fin": "2014-12-31",
            },
            {
                "annee": 2014,
                "evolution": 1.2,
                "date_debut": "2013-01-01",
                "date_fin": "2013-12-31",
            },
            {
                "annee": 2013,
                "evolution": 2.2,
                "date_debut": "2012-01-01",
                "date_fin": "2012-12-31",
            },
            {
                "annee": 2012,
                "evolution": 1.73,
                "date_debut": "2011-01-01",
                "date_fin": "2011-12-31",
            },
            {
                "annee": 2011,
                "evolution": 0.57,
                "date_debut": "2010-01-01",
                "date_fin": "2010-12-31",
            },
            {
                "annee": 2010,
                "evolution": 0.04,
                "date_debut": "2009-07-01",
                "date_fin": "2009-12-31",
            },
            {
                "annee": 2009,
                "evolution": 2.83,
                "date_debut": "2008-07-01",
                "date_fin": "2009-06-30",
            },
            {
                "annee": 2008,
                "evolution": 1.36,
                "date_debut": "2007-07-01",
                "date_fin": "2008-06-30",
            },
            {
                "annee": 2007,
                "evolution": 3.23,
                "date_debut": "2006-07-01",
                "date_fin": "2007-06-30",
            },
        ]

        for annee in data:
            for nature_logement in [
                NatureLogement.AUTRE,
                NatureLogement.RESISDENCESOCIALE,
                NatureLogement.RESIDENCEDACCUEIL,
                NatureLogement.LOGEMENTSORDINAIRES,
            ]:
                is_loyer = nature_logement == NatureLogement.LOGEMENTSORDINAIRES
                nature_logement = nature_logement if not is_loyer else None
                indice = IndiceEvolutionLoyer.objects.update_or_create(
                    annee=annee["annee"],
                    is_loyer=is_loyer,
                    nature_logement=nature_logement,
                    departements__in=(
                        [d.id for d in annee.get("departements")]
                        if annee.get("departements")
                        else []
                    ),
                    defaults=dict(
                        annee=annee["annee"],
                        is_loyer=is_loyer,
                        nature_logement=nature_logement,
                        date_debut=annee["date_debut"],
                        date_fin=annee["date_fin"],
                        evolution=annee["evolution"],
                    ),
                )[0]
                if annee.get("departements"):
                    for d in annee.get("departements"):
                        indice.departements.add(d)

    def test_compute_loyer_update_logements_ordinaires(self):
        """
        Teste que pour un logement ordinaire, le loyer est éligible à révisions
        sur différentes périodes
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=10,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2008-04-06"),
            date_actualisation=date.fromisoformat("2023-04-06"),
            departement=self.departement,
        )
        self.assertAlmostEqual(11.96, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
            departement=self.departement,
        )
        self.assertAlmostEqual(400 * 1.012, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            date_initiale=date.fromisoformat("2014-02-01"),
            departement=self.departement,
        )
        self.assertAlmostEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042 * 1.036,
            update,
            places=2,
        )

    def test_compute_loyer_update_residences_sociales(self):
        """
        Teste que pour une résidence sociale, la redevance est éligible à
        révisions sur différentes périodes
        """

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
            departement=self.departement,
        )
        self.assertAlmostEqual(400 * 1.012, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2014-02-01"),
            departement=self.departement,
        )
        self.assertAlmostEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042 * 1.036,
            update,
            places=2,
        )

    def test_compute_loyer_update_residences_d_accueil(self):
        """
        Teste que pour une résidence sociale, la redevance est éligible
        à révisions sur différentes périodes
        """
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2013-07-12"),
            date_actualisation=date.fromisoformat("2014-03-18"),
            departement=self.departement,
        )
        self.assertAlmostEqual(400 * 1.012, update, places=2)

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=100,
            nature_logement=NatureLogement.RESIDENCEDACCUEIL,
            date_initiale=date.fromisoformat("2014-02-01"),
            departement=self.departement,
        )
        self.assertAlmostEqual(
            100 * 1.0057 * 1.0008 * 1.0125 * 1.0153 * 1.0066 * 1.0042 * 1.036,
            update,
            places=2,
        )

    def test_compute_loyer_update_pensions_de_famille(self):
        """
        Teste que pour un logement de nature incompatible (pension de famille,
        résidence universitaire, hébergement) avec la calculette, une exception
        est levée
        """
        with self.assertRaises(Exception):  # noqa: B017
            LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=400,
                nature_logement=NatureLogement.PENSIONSDEFAMILLE,
                date_initiale=date.fromisoformat("2013-07-12"),
                departement=self.departement,
            )

        with self.assertRaises(Exception):  # noqa: B017
            LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=400,
                nature_logement=NatureLogement.HEBERGEMENT,
                date_initiale=date.fromisoformat("2013-07-12"),
                departement=self.departement,
            )

        with self.assertRaises(Exception):  # noqa: B017
            LoyerRedevanceUpdateComputer.compute_loyer_update(
                montant_initial=400,
                nature_logement=NatureLogement.RESIDENCEUNIVERSITAIRE,
                date_initiale=date.fromisoformat("2013-07-12"),
                departement=self.departement,
            )

    def test_compute_loyer_departements(self):
        departement = Departement.objects.get_or_create(
            code_insee="2A", nom="Corse-du-Sud"
        )[0]

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=1000,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2022-07-12"),
            date_actualisation=date.fromisoformat("2023-03-18"),
            departement=departement,
        )
        # We expect the specific 2,0 indice for this departement
        self.assertAlmostEqual(1020, update, places=2)

    def test_compute_loyer_departements_generic_case(self):
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=1000,
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            date_initiale=date.fromisoformat("2022-07-12"),
            date_actualisation=date.fromisoformat("2023-03-18"),
            departement=self.departement,
        )
        # No specific indice for this departement, we expect the generic 3.6 indice
        self.assertAlmostEqual(1036, update, places=2)
