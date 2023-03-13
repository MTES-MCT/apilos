from django.test import TestCase
from core.tests import utils_fixtures
from bailleurs.models import Bailleur, SousNatureBailleur


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

    def test_is_hlm_sem_or_type(self):
        bailleur = Bailleur.objects.order_by("uuid").first()
        for k, _ in SousNatureBailleur.choices:
            bailleur.sous_nature_bailleur = k
            bailleur.save()
            if k in [
                SousNatureBailleur.OFFICE_PUBLIC_HLM,
                SousNatureBailleur.SA_HLM_ESH,
                SousNatureBailleur.COOPERATIVE_HLM_SCIC,
            ]:
                self.assertTrue(bailleur.is_hlm())
                self.assertFalse(bailleur.is_sem())
                self.assertFalse(bailleur.is_type1and2())
            elif k in [
                SousNatureBailleur.SEM_EPL,
            ]:
                self.assertFalse(bailleur.is_hlm())
                self.assertTrue(bailleur.is_sem())
                self.assertFalse(bailleur.is_type1and2())
            else:
                self.assertFalse(bailleur.is_hlm())
                self.assertFalse(bailleur.is_sem())
                self.assertTrue(bailleur.is_type1and2())
