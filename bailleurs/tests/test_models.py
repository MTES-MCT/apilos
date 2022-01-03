from django.test import TestCase
from core.tests import utils_fixtures
from bailleurs.models import Bailleur


class BailleurModelsTest(TestCase):
    # pylint: disable=E1101 no-member
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_bailleur()

    def test_object_str(self):
        bailleur = Bailleur.objects.order_by("uuid").first()
        expected_object_name = f"{bailleur.nom}"
        self.assertEqual(str(bailleur), expected_object_name)
        self.assertEqual(bailleur.label, expected_object_name)
        self.assertEqual(bailleur.value, bailleur.id)
