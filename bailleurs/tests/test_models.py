import datetime
from django.test import TestCase
from bailleurs.models import Bailleur

class BailleurModelsTest(TestCase):
    # pylint: disable=E1101 no-member
    @classmethod
    def setUpTestData(cls):
        Bailleur.objects.create(
            nom="3F",
            siret="12345678901234",
            capital_social="SA",
            ville="Marseille",
            dg_nom="Patrick Patoulachi",
            dg_fonction="PDG",
            dg_date_deliberation=datetime.date(2014, 10, 9),
            #            operation_exceptionnelle =
        )

    def test_object_str(self):
        bailleur = Bailleur.objects.get(id=1)
        expected_object_name = f"{bailleur.nom}"
        self.assertEqual(str(bailleur), expected_object_name)
