from django.test import TestCase

from bailleurs.models import SousNatureBailleur
from bailleurs.tests.factories import BailleurFactory


class BailleurModelsTest(TestCase):
    def test_object_str(self):
        bailleur = BailleurFactory.build()
        self.assertEqual(str(bailleur), f"{bailleur.nom} ({bailleur.siren})")
        self.assertEqual(bailleur.label, bailleur.nom)
        self.assertEqual(bailleur.value, bailleur.id)

    def test_is_hlm_sem_or_type(self):
        bailleur = BailleurFactory()

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
