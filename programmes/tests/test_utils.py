from django.test import TestCase

from programmes.tests.factories import ProgrammeFactory
from programmes.utils import diff_programme_duplication


class TestDiffProgrammeDuplication(TestCase):
    def test_diff_programme_duplication(self):
        programme = ProgrammeFactory()
        duplicate = ProgrammeFactory(numero_galion=programme.numero_galion)
        self.assertEqual(
            diff_programme_duplication(programme.numero_galion),
            {"bailleur_id": sorted([programme.bailleur_id, duplicate.bailleur_id])},
        )
