from rest_framework import status
from rest_framework.test import APITestCase

from core.tests import utils_fixtures
from users.models import User
from bailleurs.models import Bailleur

BAILLEUR_READ_FIELDS = [
    "uuid",
    "nom",
    "siret",
    "adresse",
    "code_postal",
    "ville",
    "capital_social",
    "signataire_nom",
    "signataire_fonction",
    "signataire_date_deliberation",
    "type_bailleur",
    "cree_le",
    "mis_a_jour_le",
]


class SuperUserAPITest(APITestCase):
    """
    As super user, I can do anything using the API
    """

    def setUp(self):
        User.objects.create_superuser(
            "demo.bailleur", "demo.bailleur@apilos.com", "12345"
        )
        self.client.login(username="demo.bailleur", password="12345")
        (
            self.bailleur,
            self.bailleur_hlm,
            self.bailleur_sem,
        ) = utils_fixtures.create_bailleurs()

    def test_can_get_bailleur_list(self):
        response = self.client.get("/api/v1/bailleurs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_can_get_bailleur(self):
        response = self.client.get(f"/api/v1/bailleurs/{self.bailleur_hlm.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), BAILLEUR_READ_FIELDS)

    def test_can_create_bailleur(self):
        response = self.client.post(
            "/api/v1/bailleurs/",
            {
                "nom": "BAILLEUR DEMO",
                "siret": "12345678912365",
                "adresse": "5 avenue des Sauterelles",
                "code_postal": "92000",
                "ville": "Nanterre",
                "capital_social": 100000,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list(response.data.keys()), BAILLEUR_READ_FIELDS)

    def test_can_update_bailleur(self):
        response = self.client.put(
            f"/api/v1/bailleurs/{self.bailleur_hlm.uuid}/",
            {
                "nom": "BAILLEUR DEMO UPDATED",
                "siret": "12345678909876",
                "adresse": "5 rue des Sauterelles",
                "code_postal": "92012",
                "capital_social": 999999.99,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), BAILLEUR_READ_FIELDS)
        self.assertEqual(
            response.data["nom"],
            "BAILLEUR DEMO UPDATED",
        )
        self.assertEqual(
            response.data["siret"],
            "12345678909876",
        )
        self.assertEqual(
            response.data["adresse"],
            "5 rue des Sauterelles",
        )
        self.assertEqual(
            response.data["ville"],
            "Marseille",
            "ville field is not updated because not send in body",
        )
        self.assertEqual(
            response.data["capital_social"],
            999999.99,
        )

    def test_can_delete_bailleur(self):
        response = self.client.delete(f"/api/v1/bailleurs/{self.bailleur_hlm.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(list(Bailleur.objects.filter(uuid=self.bailleur_hlm.uuid)), [])
