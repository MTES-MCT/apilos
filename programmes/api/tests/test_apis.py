from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from siap.siap_client.client import build_jwt

from core.tests import utils_fixtures
from programmes.api.tests import fixtures
from programmes.models import Programme

operation_response = {
    "nom": "Programme 2",
    "bailleur": {
        "nom": "13 HABITAT",
        "siren": "782855696",
        "siret": "782855696",
        "adresse": "",
        "code_postal": "",
        "ville": "",
        "capital_social": None,
        "type_bailleur": "NONRENSEIGNE",
    },
    "administration": {
        "nom": "13055 - Métropole d'Aix-Marseille-Provence",
        "code": "13055",
        "ville_signature": None,
    },
    "conventions": [
        {
            "date_fin_conventionnement": None,
            "financement": "PLUS",
            "fond_propre": None,
            "lot": {
                "nb_logements": 1,
                "financement": "PLUS",
                "type_habitat": "COLLECTIF",
                "logements": [],
                "type_stationnements": [],
            },
            "numero": None,
            "statut": "1. Projet",
        }
    ],
    "code_postal": "13010",
    "ville": "Marseille",
    "adresse": "Rue Francois Mauriac ",
    "numero_galion": "20220600006",
    "zone_123": "A",
    "zone_abc": "02",
    "type_operation": "NEUF",
    "anru": False,
    "date_achevement_previsible": None,
    "date_achat": None,
    "date_achevement": None,
}


class OperationDetailsAPITest(APITestCase):
    """
    As super user, I can do anything using the API
    """

    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all_for_siap()

    def setUp(self):
        settings.USE_MOCKED_SIAP_CLIENT = True
        user = User.objects.create_superuser(
            "super.user", "super.user@apilos.com", "12345"
        )
        user.cerbere_login = "nicolas.oudard@beta.gouv.fr"
        user.save()

    def test_get_operation_unauthorized(self):
        client = APIClient()
        response = client.get("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        accesstoken = build_jwt(user_login="toto")
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_operation(self):
        client = APIClient()
        accesstoken = build_jwt(
            user_login="nicolas.oudard@beta.gouv.fr", habilitation_id=5
        )
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "nom": "Programme 1",
            "bailleur": fixtures.bailleur,
            "administration": fixtures.administration,
            "conventions": [fixtures.convention1, fixtures.convention2],
            "code_postal": "75007",
            "ville": "Paris",
            "adresse": "22 rue segur",
            "numero_galion": "20220600005",
            "zone_123": "3",
            "zone_abc": "B1",
            "type_operation": "NEUF",
            "anru": False,
        }
        for key, value in expected_data.items():
            self.assertEqual(response.data[key], value)
        for key in ["date_achevement_previsible", "date_achat", "date_achevement"]:
            self.assertTrue(response.data[key])

    def test_post_operation_unauthorized(self):
        client = APIClient()
        response = client.post("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        accesstoken = build_jwt(user_login="toto")
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.post("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_operation_convention(self):
        client = APIClient()
        accesstoken = build_jwt(
            user_login="nicolas.oudard@beta.gouv.fr", habilitation_id=5
        )
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)

        self.assertEqual(
            Programme.objects.filter(numero_galion="20220600006").count(), 0
        )

        response = client.post("/api-siap/v0/operation/20220600006/")

        self.assertEqual(
            Programme.objects.filter(numero_galion="20220600006").count(), 1
        )
        programme = Programme.objects.get(numero_galion="20220600006")
        self.assertEqual(programme.nom, "Programme 2")
        self.assertEqual(programme.bailleur.siret, "782855696")
        self.assertEqual(programme.conventions.count(), 1)
        self.assertEqual(response.data, operation_response)

        response = client.post("/api-siap/v0/operation/20220600006/")
        self.assertEqual(
            Programme.objects.filter(numero_galion="20220600006").count(), 1
        )
        self.assertEqual(response.data, operation_response)


class OperationClosedAPITest(APITestCase):
    """
    As super user, I can do anything using the API
    """

    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all_for_siap()

    def setUp(self):
        settings.USE_MOCKED_SIAP_CLIENT = True
        user = User.objects.create_superuser(
            "super.user", "super.user@apilos.com", "12345"
        )
        user.cerbere_login = "nicolas.oudard@beta.gouv.fr"
        user.save()

    def test_get_operation_unauthorized(self):
        client = APIClient()
        response = client.get("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        accesstoken = build_jwt(user_login="toto")
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_operation(self):
        client = APIClient()
        accesstoken = build_jwt(
            user_login="nicolas.oudard@beta.gouv.fr", habilitation_id=5
        )
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "nom": "Programme 1",
            "bailleur": fixtures.bailleur,
            "administration": fixtures.administration,
            "conventions": [fixtures.convention1, fixtures.convention2],
            "code_postal": "75007",
            "ville": "Paris",
            "adresse": "22 rue segur",
            "numero_galion": "20220600005",
            "zone_123": "3",
            "zone_abc": "B1",
            "type_operation": "NEUF",
            "anru": False,
        }
        for key, value in expected_data.items():
            self.assertEqual(response.data[key], value)
        for key in ["date_achevement_previsible", "date_achat", "date_achevement"]:
            self.assertTrue(response.data[key])

    def test_post_operation_unauthorized(self):
        client = APIClient()
        response = client.post("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        accesstoken = build_jwt(user_login="toto")
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.post("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_operation(self):
        client = APIClient()
        accesstoken = build_jwt(
            user_login="nicolas.oudard@beta.gouv.fr", habilitation_id=5
        )
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.post("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "nom": "Programme 1",
            "bailleur": fixtures.bailleur,
            "administration": fixtures.administration,
            "conventions": [fixtures.convention1, fixtures.convention2],
            "code_postal": "75007",
            "ville": "Paris",
            "adresse": "22 rue segur",
            "numero_galion": "20220600005",
            "zone_123": "3",
            "zone_abc": "B1",
            "type_operation": "NEUF",
            "anru": False,
        }
        for key, value in expected_data.items():
            self.assertEqual(response.data[key], value)
        for key in ["date_achevement_previsible", "date_achat", "date_achevement"]:
            self.assertTrue(response.data[key])
