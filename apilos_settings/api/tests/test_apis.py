from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from siap.siap_client.client import build_jwt


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class ConfigurationAPITest(APITestCase):
    """
    As super user, I can do anything using the API
    """

    def setUp(self):
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


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class ConventionKPIAPITest(APITestCase):
    fixtures = ["auth.json"]

    def test_get_convention_kpi_route_unauthorized(self):
        response = self.client.get("/api-siap/v0/convention_kpi/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_convention_kpi_route_bailleur(self):
        accesstoken = build_jwt(
            user_login="test@apilos.com", habilitation_id=5
        )  # bailleur
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/convention_kpi/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = [
            {
                "indicateur_redirection_url": "/conventions/en-cours?cstatut=1.+Projet",
                "indicateur_valeur": 0,
                "indicateur_label": "en projet",
            },
            {
                "indicateur_redirection_url": "/conventions/en-cours?cstatut=3.+Corrections+requises",
                "indicateur_valeur": 0,
                "indicateur_label": "en correction requise",
            },
            {
                "indicateur_redirection_url": "/conventions/en-cours?cstatut=4.+A+signer",
                "indicateur_valeur": 0,
                "indicateur_label": "à signer",
            },
        ]
        self.assertEqual(response.data, expected)

    def test_get_convention_kpi_route_instructeur(self):
        accesstoken = build_jwt(
            user_login="test@apilos.com", habilitation_id=12
        )  # instructeur
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/convention_kpi/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = [
            {
                "indicateur_redirection_url": "/conventions/en-cours?cstatut=2.+Instruction",
                "indicateur_valeur": 0,
                "indicateur_label": "en instruction",
            },
            {
                "indicateur_redirection_url": "/conventions/en-cours?cstatut=4.+A+signer",
                "indicateur_valeur": 0,
                "indicateur_label": "à signer",
            },
            {
                "indicateur_redirection_url": "/conventions/en-cours?cstatut=5.+Signée",
                "indicateur_valeur": 0,
                "indicateur_label": "finalisées",
            },
        ]
        self.assertEqual(response.data, expected)

    def test_get_convention_kpi_route_administrateur(self):

        accesstoken = build_jwt(
            user_login="test@apilos.com", habilitation_id=3
        )  # administrateur
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/convention_kpi/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = [
            {
                "indicateur_redirection_url": "/conventions/en-cours",
                "indicateur_valeur": 0,
                "indicateur_label": "en cours",
            },
            {
                "indicateur_redirection_url": "/conventions/en-cours?cstatut=5.+Signée",
                "indicateur_valeur": 0,
                "indicateur_label": "finalisées",
            },
        ]
        self.assertEqual(response.data, expected)
