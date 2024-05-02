from unittest.mock import Mock, patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from conventions.models import Convention
from conventions.models.choices import ConventionStatut
from conventions.tests.factories import ConventionFactory
from siap.siap_client.client import build_jwt
from users.models import User


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class ConfigurationAPITest(APITestCase):
    """
    As super user, I can do anything using the API
    """

    def setUp(self):
        user = User.objects.create_superuser(
            "super.user", "super.user@apilos.com", "12345"
        )
        user.cerbere_login = "my.name@beta.gouv.fr"
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
                "/api-siap/v0/close_operation/{NUMERO_OPERATION_SIAP}/"
            ),
            "url_acces_api_annulation_operation": (
                "/api-siap/v0/cancel_operation/{NUMERO_OPERATION_SIAP}/"
            ),
            "url_acces_api_conventions_operation": (
                "/api-siap/v0/operation/{NUMERO_OPERATION_SIAP}"
            ),
            "version": "0.0",
        }
        self.assertEqual(response.data, expected)


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
@patch("users.models.User.conventions", Mock(return_value=Convention.objects))
class ConventionKPIAPITest(ParametrizedTestCase, APITestCase):
    fixtures = ["auth.json"]

    def setUp(self) -> None:
        ConventionFactory.create_batch(3, statut=ConventionStatut.PROJET.label)
        ConventionFactory.create_batch(2, statut=ConventionStatut.INSTRUCTION.label)
        ConventionFactory.create_batch(1, statut=ConventionStatut.CORRECTION.label)
        ConventionFactory.create_batch(5, statut=ConventionStatut.A_SIGNER.label)
        ConventionFactory.create_batch(1, statut=ConventionStatut.SIGNEE.label)

    def test_get_convention_kpi_route_unauthorized(self):
        response = self.client.get("/api-siap/v0/convention_kpi/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @parametrize(
        "habilitation_id, expected_result",
        [
            param(
                12,
                [
                    {
                        "indicateur_redirection_url": "/conventions/recherche?cstatut=2. Instruction requise",
                        "indicateur_valeur": 2,
                        "indicateur_label": "en instruction",
                    },
                    {
                        "indicateur_redirection_url": "/conventions/recherche?cstatut=3. Corrections requises",
                        "indicateur_valeur": 1,
                        "indicateur_label": "en correction",
                    },
                    {
                        "indicateur_redirection_url": "/conventions/recherche?cstatut=4. A signer",
                        "indicateur_valeur": 5,
                        "indicateur_label": "à signer",
                    },
                ],
                id="instructeur",
            ),
            param(
                5,
                [
                    {
                        "indicateur_redirection_url": "/conventions/recherche?cstatut=1. Projet",
                        "indicateur_valeur": 3,
                        "indicateur_label": "en projet",
                    },
                    {
                        "indicateur_redirection_url": "/conventions/recherche?cstatut=3. Corrections requises",
                        "indicateur_valeur": 1,
                        "indicateur_label": "en correction",
                    },
                    {
                        "indicateur_redirection_url": "/conventions/recherche?cstatut=4. A signer",
                        "indicateur_valeur": 5,
                        "indicateur_label": "à signer",
                    },
                ],
                id="bailleur",
            ),
            param(
                3,
                [
                    {
                        "indicateur_redirection_url": "/conventions/recherche?cstatut="
                        + "1. Projet,2. Instruction requise,"
                        + "3. Corrections requises,4. A signer",
                        "indicateur_valeur": 11,
                        "indicateur_label": "en cours",
                    },
                ],
                id="administrateur",
            ),
        ],
    )
    def test_get_convention_kpi(self, habilitation_id, expected_result):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION="Bearer "
            + build_jwt(user_login="test@apilos.com", habilitation_id=habilitation_id)
        )
        response = client.get("/api-siap/v0/convention_kpi/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result
