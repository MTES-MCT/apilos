from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from siap.siap_client.client import build_jwt


class ConfigurationAPITest(APITestCase):
    """
    As super user, I can do anything using the API
    """

    def setUp(self):
        settings.USE_MOCKED_SIAP_CLIENT = True
        user = User.objects.create_superuser(
            "super.user", "super.user@apilos.com", "12345"
        )
        user.cerbere_login = "nicolas.oudard@beta.gouv.fr"
        user.save()

    def test_get_config_route(self):
        response = self.client.get("/api-siap/v0/config/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        accesstoken = build_jwt(user_login="toto")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/config/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            "racine_url_acces_web": "http://testserver",
            "url_acces_web_operation": "/operations/{NUMERO_OPERATION_SIAP}",
            "url_acces_web_recherche": "/conventions",
            "url_acces_api_kpi": "/api-siap/v0/convention_kpi/",
            "url_acces_api_cloture_operation": (
                "/api-siap/v0/close_operation/{NUMERO_OPERATION_SIAP}"
            ),
            "url_acces_api_conventions_operation": (
                "/api-siap/v0/operation/{NUMERO_OPERATION_SIAP}"
            ),
            "version": "0.0",
        }
        self.assertEqual(response.data, expected)
