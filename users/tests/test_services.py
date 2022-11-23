from django.test import TestCase

from core.tests import utils_fixtures
from users.services import UserService


class UserServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def test_generate_username(self):
        username = UserService.generate_username("Jeanne", "Bailleur")
        self.assertEqual(username, 'jeanne.bailleur')

        username = UserService.generate_username("Jean", "Bailleur")
        self.assertEqual(username, 'jean.bailleur2')

        username = UserService.generate_username("Chantal", "Bailleur")
        self.assertEqual(username, 'chantal.bailleur3')
