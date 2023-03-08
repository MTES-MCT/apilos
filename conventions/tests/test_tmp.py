from django.test import TestCase
from core.tests import utils_fixtures


class TmpTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs.json",
        "instructeurs.json",
        "programmes.json",
        "conventions.json",
        "users.json",
    ]

    def test_tmp(self):
        pass
