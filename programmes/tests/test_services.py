from datetime import date
from django.test import TestCase

from programmes.models import IndiceEvolutionLoyer
from programmes.services import LoyerRedevanceUpdateComputer


class LoyerRedevanceUpdateComputerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        loyers = {
            2019: 1.25,
            2020: 1.0,
            2022: 1.2,
        }

        for annee, coefficent in loyers.items():
            IndiceEvolutionLoyer.objects.update_or_create(
                annee=annee, defaults=dict(annee=annee, coefficient=coefficent)
            )

    def test_compute_loyer_update(self):
        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400,
            date_initiale=date.fromisoformat("2018-10-20"),
            date_actualisation=date.fromisoformat("2020-03-18"),
        )
        self.assertEqual(500, update)

        print(IndiceEvolutionLoyer.objects.all())

        update = LoyerRedevanceUpdateComputer.compute_loyer_update(
            montant_initial=400, date_initiale=date.fromisoformat("2018-10-20")
        )
        self.assertEqual(600, update)
