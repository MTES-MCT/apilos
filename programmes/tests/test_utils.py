from django.test import TestCase

from core.tests import utils_fixtures
from programmes.utils import diff_programme_duplication


class TestDiffProgrammeDuplication(TestCase):
    def test_diff_programme_duplication(self):
        bailleur_1 = utils_fixtures.create_bailleur(siret="111111111")
        programme_1 = utils_fixtures.create_programme(bailleur_1)

        bailleur_2 = utils_fixtures.create_bailleur(siret="222222222")
        programme_2 = utils_fixtures.create_programme(bailleur_2)

        self.assertEqual(programme_1.numero_galion, programme_2.numero_galion)

        self.assertEqual(
            diff_programme_duplication(programme_1.numero_galion),
            {"bailleur_id": [bailleur_1.id, bailleur_2.id]},
        )
