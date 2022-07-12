from typing import OrderedDict
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from siap.siap_client.client import build_jwt

from core.tests import utils_fixtures


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
            "bailleur": OrderedDict(
                [
                    ("nom", "3F"),
                    ("siren", None),
                    ("siret", "12345678901234"),
                    ("adresse", None),
                    ("code_postal", None),
                    ("ville", "Marseille"),
                    ("capital_social", 123000.5),
                    ("type_bailleur", "NONRENSEIGNE"),
                ]
            ),
            "administration": OrderedDict(
                [
                    ("nom", "CA d'Arles-Crau-Camargue-Montagnette"),
                    ("code", "12345"),
                    ("ville_signature", None),
                ]
            ),
            "conventions": [
                OrderedDict(
                    [
                        ("date_fin_conventionnement", None),
                        ("financement", "PLUS"),
                        ("fond_propre", None),
                        (
                            "lot",
                            OrderedDict(
                                [
                                    ("nb_logements", None),
                                    ("financement", "PLUS"),
                                    ("type_habitat", "COLLECTIF"),
                                    (
                                        "logements",
                                        [
                                            OrderedDict(
                                                [
                                                    ("designation", "PLUS 1"),
                                                    ("typologie", "T1"),
                                                    ("surface_habitable", "50.00"),
                                                    ("surface_annexes", "20.00"),
                                                    (
                                                        "surface_annexes_retenue",
                                                        "10.00",
                                                    ),
                                                    ("surface_utile", "60.00"),
                                                    ("loyer_par_metre_carre", "5.50"),
                                                    ("coeficient", "0.9000"),
                                                    ("loyer", "297.00"),
                                                    ("annexes", []),
                                                ]
                                            )
                                        ],
                                    ),
                                    ("type_stationnements", []),
                                ]
                            ),
                        ),
                        ("numero", "0001"),
                        ("statut", "1. Projet"),
                    ]
                ),
                OrderedDict(
                    [
                        ("date_fin_conventionnement", None),
                        ("financement", "PLAI"),
                        ("fond_propre", None),
                        (
                            "lot",
                            OrderedDict(
                                [
                                    ("nb_logements", None),
                                    ("financement", "PLAI"),
                                    ("type_habitat", "MIXTE"),
                                    (
                                        "logements",
                                        [
                                            OrderedDict(
                                                [
                                                    ("designation", "PLAI 1"),
                                                    ("typologie", "T1"),
                                                    ("surface_habitable", "50.00"),
                                                    ("surface_annexes", "20.00"),
                                                    (
                                                        "surface_annexes_retenue",
                                                        "10.00",
                                                    ),
                                                    ("surface_utile", "60.00"),
                                                    ("loyer_par_metre_carre", "5.50"),
                                                    ("coeficient", "0.9000"),
                                                    ("loyer", "297.00"),
                                                    (
                                                        "annexes",
                                                        [
                                                            OrderedDict(
                                                                [
                                                                    (
                                                                        "typologie",
                                                                        "CAVE",
                                                                    ),
                                                                    (
                                                                        "surface_hors_surface_retenue",
                                                                        "5.00",
                                                                    ),
                                                                    (
                                                                        "loyer_par_metre_carre",
                                                                        "0.10",
                                                                    ),
                                                                    ("loyer", "0.50"),
                                                                ]
                                                            ),
                                                            OrderedDict(
                                                                [
                                                                    (
                                                                        "typologie",
                                                                        "JARDIN",
                                                                    ),
                                                                    (
                                                                        "surface_hors_surface_retenue",
                                                                        "5.00",
                                                                    ),
                                                                    (
                                                                        "loyer_par_metre_carre",
                                                                        "0.10",
                                                                    ),
                                                                    ("loyer", "0.50"),
                                                                ]
                                                            ),
                                                        ],
                                                    ),
                                                ]
                                            ),
                                            OrderedDict(
                                                [
                                                    ("designation", "PLAI 2"),
                                                    ("typologie", "T2"),
                                                    ("surface_habitable", "50.00"),
                                                    ("surface_annexes", "20.00"),
                                                    (
                                                        "surface_annexes_retenue",
                                                        "10.00",
                                                    ),
                                                    ("surface_utile", "60.00"),
                                                    ("loyer_par_metre_carre", "5.50"),
                                                    ("coeficient", "0.9000"),
                                                    ("loyer", "297.00"),
                                                    ("annexes", []),
                                                ]
                                            ),
                                            OrderedDict(
                                                [
                                                    ("designation", "PLAI 3"),
                                                    ("typologie", "T3"),
                                                    ("surface_habitable", "50.00"),
                                                    ("surface_annexes", "20.00"),
                                                    (
                                                        "surface_annexes_retenue",
                                                        "10.00",
                                                    ),
                                                    ("surface_utile", "60.00"),
                                                    ("loyer_par_metre_carre", "5.50"),
                                                    ("coeficient", "0.9000"),
                                                    ("loyer", "297.00"),
                                                    ("annexes", []),
                                                ]
                                            ),
                                        ],
                                    ),
                                    ("type_stationnements", []),
                                ]
                            ),
                        ),
                        ("numero", "0002"),
                        ("statut", "1. Projet"),
                    ]
                ),
            ],
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

        # client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        # response = client.get("/api-siap/v0/config/")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # expected = {
        #     "racine_url_acces_web": "http://testserver",
        #     "url_acces_web_operation": "/operations/{NUMERO_OPERATION_SIAP}",
        #     "url_acces_web_recherche": "/conventions",
        #     "url_acces_api_kpi": "/api-siap/v0/convention_kpi/",
        #     "version": "0.0",
        # }
        # self.assertEqual(response.data, expected)
