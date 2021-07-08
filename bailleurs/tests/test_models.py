from django.test import TestCase
from bailleurs.models import Bailleur
import datetime

class BailleursModelsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Bailleur.objects.create(
            nom = "3F",
            siret = "12345678901234",
            capital_social = "SA",
            siege = "Marseille",
            dg_nom = "Patrick Patoulachi",
            dg_fonction = "PDG",
            dg_date_deliberation = datetime.date(2014, 10, 9),
#            operation_exceptionnelle = 
        )

    def test_object_name_is_last_name_comma_first_name(self):
        bailleur = Bailleur.objects.get(id=1)
        expected_object_name = f'{bailleur.nom}'
        self.assertEqual(str(bailleur), expected_object_name)

    def test_get_absolute_url(self):
        bailleur = Bailleur.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(bailleur.get_absolute_url(), f'/bailleurs/{bailleur.uuid}')
