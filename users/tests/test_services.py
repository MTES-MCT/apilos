from django.test import TestCase

from users.services import UserService


class UserServiceTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_extract_username_from_email(self):
        username = UserService.extract_username_from_email("jeanne.bailleur@apilos.com")
        self.assertEqual(username, "jeanne.bailleur")

        username = UserService.extract_username_from_email("jean.bailleur2@apilos.com")
        self.assertEqual(username, "jean.bailleur2")

        username = UserService.extract_username_from_email("vélomoteur")
        self.assertEqual(username, "")
