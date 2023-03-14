import json
from operator import itemgetter

from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention

from users.models import User
from siap.siap_client.client import build_jwt

from core.tests import utils_fixtures
from programmes.api.tests import fixtures
from programmes.models import Programme


operation_response = {
    **fixtures.programme2,
    "bailleur": {
        "nom": "13 HABITAT",
        "siren": "782855696",
        "siret": "782855696",
        "adresse": "",
        "code_postal": "",
        "ville": "MARSEILLE 4",
        "capital_social": None,
        "sous_nature_bailleur": "NONRENSEIGNE",
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
            "operation_version": fixtures.programme2,
        }
    ],
}


class OperationDetailsAPITest(APITestCase):
    fixtures = ["departements.json"]

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
    fixtures = ["departements.json"]
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
            "bailleur": {
                "nom": "3F",
                "siren": "123456789",
                "siret": "12345678901234",
                "adresse": None,
                "code_postal": None,
                "ville": "Marseille",
                "capital_social": 123000.5,
                "sous_nature_bailleur": "NONRENSEIGNE",
            },
            "administration": {
                "nom": "CA d'Arles-Crau-Camargue-Montagnette",
                "code": "12345",
                "ville_signature": None,
            },
            "code_postal": "75007",
            "ville": "Paris",
            "adresse": "22 rue segur",
            "numero_galion": "20220600005",
            "zone_123": "3",
            "zone_abc": "B1",
            "type_operation": "NEUF",
            "anru": False,
            "date_achevement_previsible": "2024-01-02",
            "date_achat": "2022-01-02",
            "date_achevement": "2024-04-11",
            "all_conventions_are_signed": False,
            "last_conventions_state": [],
        }
        expected_conventions = [
            {
                "date_fin_conventionnement": None,
                "financement": "PLUS",
                "fond_propre": None,
                "lot": {
                    "nb_logements": None,
                    "financement": "PLUS",
                    "type_habitat": "COLLECTIF",
                    "logements": [
                        {
                            "designation": "PLUS 1",
                            "typologie": "T1",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        }
                    ],
                    "type_stationnements": [],
                },
                "operation_version": {
                    "nom": "Programme 1",
                    "code_postal": "75007",
                    "ville": "Paris",
                    "adresse": "22 rue segur",
                    "numero_galion": "20220600005",
                    "zone_123": "3",
                    "zone_abc": "B1",
                    "type_operation": "NEUF",
                    "anru": False,
                    "date_achevement_previsible": "2024-01-02",
                    "date_achat": "2022-01-02",
                    "date_achevement": "2024-04-11",
                },
                "numero": "0001",
                "statut": "1. Projet",
            },
            {
                "date_fin_conventionnement": None,
                "financement": "PLAI",
                "fond_propre": None,
                "lot": {
                    "nb_logements": None,
                    "financement": "PLAI",
                    "type_habitat": "MIXTE",
                    "logements": [
                        {
                            "designation": "PLAI 1",
                            "typologie": "T1",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [
                                {
                                    "typologie": "COUR",
                                    "surface_hors_surface_retenue": "5.00",
                                    "loyer_par_metre_carre": "0.10",
                                    "loyer": "0.50",
                                },
                                {
                                    "typologie": "JARDIN",
                                    "surface_hors_surface_retenue": "5.00",
                                    "loyer_par_metre_carre": "0.10",
                                    "loyer": "0.50",
                                },
                            ],
                        },
                        {
                            "designation": "PLAI 2",
                            "typologie": "T2",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        },
                        {
                            "designation": "PLAI 3",
                            "typologie": "T3",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        },
                    ],
                    "type_stationnements": [],
                },
                "operation_version": {
                    "nom": "Programme 1",
                    "code_postal": "75007",
                    "ville": "Paris",
                    "adresse": "22 rue segur",
                    "numero_galion": "20220600005",
                    "zone_123": "3",
                    "zone_abc": "B1",
                    "type_operation": "NEUF",
                    "anru": False,
                    "date_achevement_previsible": "2024-01-02",
                    "date_achat": "2022-01-02",
                    "date_achevement": "2024-04-11",
                },
                "numero": "0002",
                "statut": "1. Projet",
            },
        ]
        returned_conventions = response.data.pop("conventions")
        self.assertEqual(response.data, expected_data)

        self.assertEqual(
            sorted(returned_conventions, key=itemgetter("numero")), expected_conventions
        )

    def test_get_operation_convention_signed(self):
        Convention.objects.filter(numero__in=["0001", "0002"]).update(
            statut=ConventionStatut.SIGNEE
        )
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
            "code_postal": "75007",
            "ville": "Paris",
            "adresse": "22 rue segur",
            "numero_galion": "20220600005",
            "zone_123": "3",
            "zone_abc": "B1",
            "type_operation": "NEUF",
            "anru": False,
            "date_achevement_previsible": "2024-01-02",
            "date_achat": "2022-01-02",
            "date_achevement": "2024-04-11",
            "all_conventions_are_signed": True,
        }
        expected_convention_list = [
            {
                "date_fin_conventionnement": None,
                "financement": "PLUS",
                "fond_propre": None,
                "lot": {
                    "nb_logements": None,
                    "financement": "PLUS",
                    "type_habitat": "COLLECTIF",
                    "logements": [
                        {
                            "designation": "PLUS 1",
                            "typologie": "T1",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        }
                    ],
                    "type_stationnements": [],
                },
                "operation_version": {
                    "nom": "Programme 1",
                    "code_postal": "75007",
                    "ville": "Paris",
                    "adresse": "22 rue segur",
                    "numero_galion": "20220600005",
                    "zone_123": "3",
                    "zone_abc": "B1",
                    "type_operation": "NEUF",
                    "anru": False,
                    "date_achevement_previsible": "2024-01-02",
                    "date_achat": "2022-01-02",
                    "date_achevement": "2024-04-11",
                },
                "numero": "0001",
                "statut": "5. Signée",
            },
            {
                "date_fin_conventionnement": None,
                "financement": "PLAI",
                "fond_propre": None,
                "lot": {
                    "nb_logements": None,
                    "financement": "PLAI",
                    "type_habitat": "MIXTE",
                    "logements": [
                        {
                            "designation": "PLAI 1",
                            "typologie": "T1",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [
                                {
                                    "typologie": "COUR",
                                    "surface_hors_surface_retenue": "5.00",
                                    "loyer_par_metre_carre": "0.10",
                                    "loyer": "0.50",
                                },
                                {
                                    "typologie": "JARDIN",
                                    "surface_hors_surface_retenue": "5.00",
                                    "loyer_par_metre_carre": "0.10",
                                    "loyer": "0.50",
                                },
                            ],
                        },
                        {
                            "designation": "PLAI 2",
                            "typologie": "T2",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        },
                        {
                            "designation": "PLAI 3",
                            "typologie": "T3",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        },
                    ],
                    "type_stationnements": [],
                },
                "operation_version": {
                    "nom": "Programme 1",
                    "code_postal": "75007",
                    "ville": "Paris",
                    "adresse": "22 rue segur",
                    "numero_galion": "20220600005",
                    "zone_123": "3",
                    "zone_abc": "B1",
                    "type_operation": "NEUF",
                    "anru": False,
                    "date_achevement_previsible": "2024-01-02",
                    "date_achat": "2022-01-02",
                    "date_achevement": "2024-04-11",
                },
                "numero": "0002",
                "statut": "5. Signée",
            },
        ]
        last_conventions_states = response.data.pop("last_conventions_state")
        conventions = response.data.pop("conventions")
        self.assertEqual(response.data, expected_data)

        self.assertEqual(
            sorted(last_conventions_states, key=itemgetter("numero")),
            expected_convention_list,
        )
        self.assertEqual(
            sorted(conventions, key=itemgetter("numero")),
            expected_convention_list,
        )

        for key, value in expected_data.items():
            self.assertEqual(response.data[key], value)
        for key in ["date_achevement_previsible", "date_achat", "date_achevement"]:
            self.assertTrue(response.data[key])

    def test_get_operation_with_avenant(self):
        Convention.objects.filter(numero__in=["0001", "0002"]).update(
            statut=ConventionStatut.SIGNEE
        )
        user = User.objects.get(cerbere_login="nicolas.oudard@beta.gouv.fr")
        convention1 = Convention.objects.get(numero="0001")
        avenant1 = convention1.clone(user, convention_origin=convention1)

        client = APIClient()
        accesstoken = build_jwt(
            user_login="nicolas.oudard@beta.gouv.fr", habilitation_id=5
        )
        client.credentials(HTTP_AUTHORIZATION="Bearer " + accesstoken)
        response = client.get("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["conventions"]), 3)
        self.assertFalse(response.data["all_conventions_are_signed"])

        expected_last_conventions_state = [
            {
                "date_fin_conventionnement": None,
                "financement": "PLUS",
                "fond_propre": None,
                "lot": {
                    "nb_logements": None,
                    "financement": "PLUS",
                    "type_habitat": "COLLECTIF",
                    "logements": [
                        {
                            "designation": "PLUS 1",
                            "typologie": "T1",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        }
                    ],
                    "type_stationnements": [],
                },
                "operation_version": {
                    "nom": "Programme 1",
                    "code_postal": "75007",
                    "ville": "Paris",
                    "adresse": "22 rue segur",
                    "numero_galion": "20220600005",
                    "zone_123": "3",
                    "zone_abc": "B1",
                    "type_operation": "NEUF",
                    "anru": False,
                    "date_achevement_previsible": "2024-01-02",
                    "date_achat": "2022-01-02",
                    "date_achevement": "2024-04-11",
                },
                "numero": "0001",
                "statut": "5. Signée",
            },
            {
                "date_fin_conventionnement": None,
                "financement": "PLAI",
                "fond_propre": None,
                "lot": {
                    "nb_logements": None,
                    "financement": "PLAI",
                    "type_habitat": "MIXTE",
                    "logements": [
                        {
                            "designation": "PLAI 1",
                            "typologie": "T1",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [
                                {
                                    "typologie": "COUR",
                                    "surface_hors_surface_retenue": "5.00",
                                    "loyer_par_metre_carre": "0.10",
                                    "loyer": "0.50",
                                },
                                {
                                    "typologie": "JARDIN",
                                    "surface_hors_surface_retenue": "5.00",
                                    "loyer_par_metre_carre": "0.10",
                                    "loyer": "0.50",
                                },
                            ],
                        },
                        {
                            "designation": "PLAI 2",
                            "typologie": "T2",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        },
                        {
                            "designation": "PLAI 3",
                            "typologie": "T3",
                            "surface_habitable": "50.00",
                            "surface_annexes": "20.00",
                            "surface_annexes_retenue": "10.00",
                            "surface_utile": "60.00",
                            "loyer_par_metre_carre": "5.50",
                            "coeficient": "0.9000",
                            "loyer": "297.00",
                            "annexes": [],
                        },
                    ],
                    "type_stationnements": [],
                },
                "operation_version": {
                    "nom": "Programme 1",
                    "code_postal": "75007",
                    "ville": "Paris",
                    "adresse": "22 rue segur",
                    "numero_galion": "20220600005",
                    "zone_123": "3",
                    "zone_abc": "B1",
                    "type_operation": "NEUF",
                    "anru": False,
                    "date_achevement_previsible": "2024-01-02",
                    "date_achat": "2022-01-02",
                    "date_achevement": "2024-04-11",
                },
                "numero": "0002",
                "statut": "5. Signée",
            },
        ]

        self.assertEqual(
            sorted(response.data["last_conventions_state"], key=itemgetter("numero")),
            expected_last_conventions_state,
        )

        avenant1.lot.nb_logements = 10
        avenant1.lot.save()
        avenant1.statut = ConventionStatut.SIGNEE
        avenant1.save()

        response = client.get("/api-siap/v0/close_operation/20220600005/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["conventions"]), 3)
        self.assertTrue(response.data["all_conventions_are_signed"])
        self.assertEqual(len(response.data["last_conventions_state"]), 2)
        self.assertEqual(
            list(
                filter(
                    lambda x: x["numero"] is None,
                    response.data["last_conventions_state"],
                )
            )[0]["lot"]["nb_logements"],
            10,
        )

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
            # "conventions": [fixtures.convention1, fixtures.convention2],
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
