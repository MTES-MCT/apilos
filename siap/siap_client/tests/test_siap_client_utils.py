from django.test import TestCase

from bailleurs.models import Bailleur
from core.tests import utils_fixtures
from instructeurs.models import Administration
from programmes.models.choices import NatureLogement, TypeOperation
from siap.exceptions import (
    InconsistentDataSIAPException,
    NoConventionForOperationSIAPException,
)
from siap.siap_client import utils
from users.models import User


class GetAddressFromLocdataTest(TestCase):
    def test__get_address_from_locdata_empty(self):
        self.assertRaises(KeyError, utils._get_address_from_locdata, {})
        self.assertRaises(
            KeyError, utils._get_address_from_locdata, {"adresseComplete": {}}
        )
        adresse, code_postal, ville = utils._get_address_from_locdata({"adresse": ""})
        self.assertEqual(adresse, "")
        self.assertEqual(code_postal, "")
        self.assertEqual(ville, "")
        adresse, code_postal, ville = utils._get_address_from_locdata(
            {
                "adresseComplete": {
                    "adresse": "",
                    "codePostal": "",
                    "commune": "",
                }
            }
        )
        self.assertEqual(adresse, "")
        self.assertEqual(code_postal, "")
        self.assertEqual(ville, "")

    def test__get_address_from_locdata_adresse_complete(self):
        donneesLocalisation = {
            "adresse": "fake adresse",
            "adresseComplete": {
                "adresse": "10 rue fake",
                "codePostal": "01000",
                "commune": "Vile-sur-fake ok",
            },
        }
        adresse, code_postal, ville = utils._get_address_from_locdata(
            donneesLocalisation
        )
        self.assertEqual(adresse, "10 rue fake")
        self.assertEqual(code_postal, "01000")
        self.assertEqual(ville, "Vile-sur-fake ok")

    def test__get_address_from_locdata_adresse_fallback(self):
        adresse, code_postal, ville = utils._get_address_from_locdata(
            {"adresse": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."}
        )
        self.assertEqual(
            adresse, "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )
        self.assertEqual(code_postal, "")
        self.assertEqual(ville, "")
        adresse, code_postal, ville = utils._get_address_from_locdata(
            {"adresse": "145, rue des chamallow  13015 MarSeille CEDEX 15"}
        )
        self.assertEqual(adresse, "145, rue des chamallow")
        self.assertEqual(code_postal, "13015")
        self.assertEqual(ville, "MarSeille CEDEX 15")


class GetOrCreateProgrammeTest(TestCase):
    data_from_siap = {
        "donneesLocalisation": {
            "region": {"codeInsee": "93", "libelle": None},
            "departement": {"codeInsee": "13", "libelle": None},
            "commune": {"codeInsee": "13001", "libelle": "Aix-en-Provence"},
            "adresse": "10 Avenue du General Koenig 13100 Aix-en-Provence",
            "adresseComplete": {
                "adresse": "10 Avenue du General Koenig ",
                "codePostal": "13100",
                "commune": "Aix-en-Provence",
                "codePostalCommune": "13100 Aix-en-Provence",
            },
            "zonage123": "02",
            "zonageABC": "A",
        },
        "detailsOperation": [
            {"aide": {"code": "PLAI", "libelle": "PLAI"}},
            {"aide": {"code": "PLUS", "libelle": "PLUS"}},
        ],
        "donneesOperation": {
            "nomOperation": "Sans travaux 2022-10-07",
            "numeroOperation": "20221000003",
            "aides": [],
            "sousNatureOperation": None,
            "typeConstruction": None,
            "natureLogement": "LOO",
            "sansTravaux": False,
        },
    }

    def setUp(self):
        utils_fixtures.create_administrations()
        utils_fixtures.create_bailleurs()

    def test_get_or_create(self):
        programme = utils.get_or_create_programme(
            self.data_from_siap,
            Bailleur.objects.first(),
            Administration.objects.first(),
        )
        self.assertTrue(programme.uuid)
        self.assertEqual(programme.nature_logement, NatureLogement.LOGEMENTSORDINAIRES)

    def test_get_or_create_no_details_failed(self):
        data_from_siap = {**self.data_from_siap}
        del data_from_siap["detailsOperation"]

        self.assertRaises(
            NoConventionForOperationSIAPException,
            utils.get_or_create_programme,
            data_from_siap,
            Bailleur.objects.first(),
            Administration.objects.first(),
        )

    def test_get_or_create_sans_travaux(self):
        data_from_siap = {**self.data_from_siap}
        data_from_siap["donneesOperation"]["sansTravaux"] = True
        del data_from_siap["detailsOperation"]
        programme = utils.get_or_create_programme(
            data_from_siap,
            Bailleur.objects.first(),
            Administration.objects.first(),
        )
        self.assertTrue(programme.uuid)
        self.assertEqual(programme.type_operation, TypeOperation.SANSTRAVAUX)

    def test_get_or_create_no_nature_failed(self):
        data_from_siap = {**self.data_from_siap}
        data_from_siap["donneesOperation"]["natureLogement"] = None
        self.data_from_siap["detailsOperation"] = (
            [
                {"aide": {"code": "PLAI", "libelle": "PLAI"}},
                {"aide": {"code": "PLUS", "libelle": "PLUS"}},
            ],
        )
        self.assertRaises(
            InconsistentDataSIAPException,
            utils.get_or_create_programme,
            self.data_from_siap,
            Bailleur.objects.first(),
            Administration.objects.first(),
        )

    def test_get_or_create_no_convention(self):
        data_from_siap = {
            **self.data_from_siap,
            "detailsOperation": [
                {"aide": {"code": "FAKE1", "libelle": "FAKE1"}},
                {"aide": {"code": "FAKE2", "libelle": "FAKE2"}},
            ],
        }
        self.assertRaises(
            NoConventionForOperationSIAPException,
            utils.get_or_create_programme,
            data_from_siap,
            Bailleur.objects.first(),
            Administration.objects.first(),
        )


class GetOrCreateConventionFromOperationTest(TestCase):
    def test_raises_when_unknown_aide(self):
        self.assertRaises(
            NoConventionForOperationSIAPException,
            utils.get_or_create_conventions,
            {
                "detailsOperation": [
                    {"aide": {"code": "FAKE1", "libelle": "FAKE1"}},
                    {"aide": {"code": "FAKE2", "libelle": "FAKE2"}},
                ]
            },
            User.objects.first(),
        )

    def test_dont_raises_when_known_aide(self):
        # doesn't raise with NoConventionForOperationSIAPException
        try:
            utils.get_or_create_conventions(
                {
                    "detailsOperation": [
                        {"aide": {"code": "PLAI", "libelle": "PLAI"}},
                        {"aide": {"code": "FAKE1", "libelle": "FAKE1"}},
                    ]
                },
                User.objects.first(),
            )
        except Exception as exception:
            self.assertNotEqual(exception, NoConventionForOperationSIAPException)
