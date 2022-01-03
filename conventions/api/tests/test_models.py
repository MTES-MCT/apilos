# pylint: disable=R0902,E1101

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests import utils_fixtures
from programmes.models import Financement
from users.models import User, Role
from users.type_models import TypeRole

CONVENTION_READ_FIELDS = [
    "uuid",
    "numero",
    "bailleur",
    "programme",
    "lot",
]


class SuperUserAPITest(APITestCase):
    """
    As super user, I can read any convention
    """

    def setUp(self):
        User.objects.create_superuser("nico", "nico@apilos.com", "12345")
        self.client.login(username="nico", password="12345")
        (
            self.administration_arles,
            self.administration_marseille,
        ) = utils_fixtures.create_administrations()
        (self.bailleur, self.bailleur_hlm) = utils_fixtures.create_bailleurs()
        programme = utils_fixtures.create_programme(
            self.bailleur, self.administration_arles, nom="Programe 1"
        )
        lot_plai = utils_fixtures.create_lot(programme, Financement.PLAI)
        lot_plus = utils_fixtures.create_lot(programme, Financement.PLUS)
        self.convention1 = utils_fixtures.create_convention(lot_plus, numero="0001")
        self.convention2 = utils_fixtures.create_convention(lot_plai, numero="0002")

    def test_can_get_convention_list(self):
        response = self.client.get("/api/v1/conventions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_can_get_convention(self):
        response = self.client.get(f"/api/v1/conventions/{self.convention1.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), CONVENTION_READ_FIELDS)
        self.assertEqual(response.data["numero"], "0001")

    def test_create_convention_doesnot_exist(self):
        response = self.client.post(
            "/api/v1/conventions/",
            {"numero": "test"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_convention_doesnot_exist(self):
        response = self.client.put(
            f"/api/v1/conventions/{self.convention1.uuid}/",
            {"numero": "test"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_convention_doesnot_exist(self):
        response = self.client.delete(f"/api/v1/conventions/{self.convention1.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class InstructeurUserAPITest(APITestCase):
    """
    As instructeur, I am able to read the conventions of my administration
    """

    def setUp(self):
        user_instructeur = User.objects.create_user(
            "sabine", "sabine@apilos.com", "12345"
        )
        self.client.login(username="sabine", password="12345")
        (
            self.administration_arles,
            self.administration_marseille,
        ) = utils_fixtures.create_administrations()
        group_instructeur = utils_fixtures.create_group(
            "Instructeur", rwd=["convention"]
        )
        Role.objects.create(
            typologie=TypeRole.INSTRUCTEUR,
            user=user_instructeur,
            administration=self.administration_arles,
            group=group_instructeur,
        )
        (self.bailleur, self.bailleur_hlm) = utils_fixtures.create_bailleurs()

        programme_arles = utils_fixtures.create_programme(
            self.bailleur, self.administration_arles, nom="Programe 1"
        )
        lot_plai_arles = utils_fixtures.create_lot(programme_arles, Financement.PLAI)
        lot_plus_arles = utils_fixtures.create_lot(programme_arles, Financement.PLUS)
        lot_pls_arles = utils_fixtures.create_lot(programme_arles, Financement.PLS)
        self.convention1 = utils_fixtures.create_convention(
            lot_plus_arles, numero="ARLES 0001"
        )
        self.convention2 = utils_fixtures.create_convention(
            lot_plai_arles, numero="ARLES 0002"
        )
        self.convention3 = utils_fixtures.create_convention(
            lot_pls_arles, numero="ARLES 0003"
        )

        programme_marseille = utils_fixtures.create_programme(
            self.bailleur, self.administration_marseille, nom="Programe Marseille"
        )
        lot_plai_marseille = utils_fixtures.create_lot(
            programme_marseille, Financement.PLAI
        )
        lot_plus_marseille = utils_fixtures.create_lot(
            programme_marseille, Financement.PLUS
        )
        self.convention4 = utils_fixtures.create_convention(
            lot_plus_marseille, numero="MARSEILLE 0001"
        )
        self.convention5 = utils_fixtures.create_convention(
            lot_plai_marseille, numero="MARSEILLE 0002"
        )

    def test_can_get_convention_list(self):
        response = self.client.get("/api/v1/conventions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_can_get_convention(self):
        response = self.client.get(f"/api/v1/conventions/{self.convention1.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), CONVENTION_READ_FIELDS)
        self.assertEqual(response.data["numero"], "ARLES 0001")
        response = self.client.get(f"/api/v1/conventions/{self.convention4.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_convention_doesnot_exist(self):
        response = self.client.post(
            "/api/v1/conventions/",
            {"numero": "test"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_convention_doesnot_exist(self):
        response = self.client.put(
            f"/api/v1/conventions/{self.convention1.uuid}/",
            {"numero": "test"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_convention_doesnot_exist(self):
        response = self.client.delete(f"/api/v1/conventions/{self.convention1.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BailleurUserAPITest(APITestCase):
    """
    As bailleur, I am able to read the conventions of my bailleur companies
    """

    def setUp(self):
        user_bailleur = User.objects.create_user("raph", "raph@apilos.com", "12345")
        self.client.login(username="raph", password="12345")
        (
            self.administration_arles,
            self.administration_marseille,
        ) = utils_fixtures.create_administrations()
        (self.bailleur, self.bailleur_hlm) = utils_fixtures.create_bailleurs()
        group_bailleur = utils_fixtures.create_group("Bailleur", rwd=["convention"])
        Role.objects.create(
            typologie=TypeRole.BAILLEUR,
            bailleur=self.bailleur_hlm,
            user=user_bailleur,
            group=group_bailleur,
        )

        programme_arles = utils_fixtures.create_programme(
            self.bailleur, self.administration_arles, nom="Programe 1"
        )
        lot_plai_arles = utils_fixtures.create_lot(programme_arles, Financement.PLAI)
        lot_plus_arles = utils_fixtures.create_lot(programme_arles, Financement.PLUS)
        lot_pls_arles = utils_fixtures.create_lot(programme_arles, Financement.PLS)
        self.convention1 = utils_fixtures.create_convention(
            lot_plus_arles, numero="ARLES 0001"
        )
        self.convention2 = utils_fixtures.create_convention(
            lot_plai_arles, numero="ARLES 0002"
        )
        self.convention3 = utils_fixtures.create_convention(
            lot_pls_arles, numero="ARLES 0003"
        )

        programme_marseille = utils_fixtures.create_programme(
            self.bailleur_hlm, self.administration_marseille, nom="Programe Marseille"
        )
        lot_plai_marseille = utils_fixtures.create_lot(
            programme_marseille, Financement.PLAI
        )
        lot_plus_marseille = utils_fixtures.create_lot(
            programme_marseille, Financement.PLUS
        )
        self.convention4 = utils_fixtures.create_convention(
            lot_plus_marseille, numero="MARSEILLE 0001"
        )
        self.convention5 = utils_fixtures.create_convention(
            lot_plai_marseille, numero="MARSEILLE 0002"
        )

    def test_can_get_convention_list(self):
        response = self.client.get("/api/v1/conventions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_can_get_convention(self):
        response = self.client.get(f"/api/v1/conventions/{self.convention4.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), CONVENTION_READ_FIELDS)
        self.assertEqual(response.data["numero"], "MARSEILLE 0001")
        response = self.client.get(f"/api/v1/conventions/{self.convention3.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_convention_doesnot_exist(self):
        response = self.client.post(
            "/api/v1/conventions/",
            {"numero": "test"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_convention_doesnot_exist(self):
        response = self.client.put(
            f"/api/v1/conventions/{self.convention3.uuid}/",
            {"numero": "test"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_convention_doesnot_exist(self):
        response = self.client.delete(f"/api/v1/conventions/{self.convention3.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
