from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class ConfigurationAPITest(APITestCase):
    """
    As super user, I can do anything using the API
    """

    def setUp(self):
        User.objects.create_superuser("super.user", "super.user@apilos.com", "12345")

    def test_can_get_bailleur_list(self):
        response = self.client.get("/api-siap/v0/config/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username="super.user", password="12345")
        response = self.client.get("/api-siap/v0/config/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            "racine_url_acces_web": "http://testserver",
            "url_acces_web_operation": "/operations/{NUMERO_OPEPERATION_SIAP}",
            "url_acces_web_recherche": "/conventions",
            "version": "0.0",
        }
        self.assertEqual(response.data, expected)
