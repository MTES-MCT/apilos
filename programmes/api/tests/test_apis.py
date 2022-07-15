from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from siap.siap_client.client import build_jwt

from core.tests import utils_fixtures
from . import test_fixtures


class ConfigurationAPITest(APITestCase):
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

    def test_get_config_route(self):
        client = APIClient()
        response = client.get("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        accesstoken = build_jwt(user_login="toto")
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # accesstoken = build_jwt(user_login="nicolas.oudard@beta.gouv.fr", habilitation_id=1)
        # client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        # response = client.get("/api-siap/v0/operation/20220600005/")
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        accesstoken = build_jwt(
            user_login="nicolas.oudard@beta.gouv.fr", habilitation_id=5
        )
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "nom": "Programe 1",
            "bailleur": test_fixtures.bailleur,
            "administration": test_fixtures.administration,
            "conventions": [test_fixtures.convention1, test_fixtures.convention2],
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
