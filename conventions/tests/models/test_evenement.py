from django.test import TestCase
from django.utils import timezone

from conventions.models import Convention, TypeEvenement


class EvenementModelsTest(TestCase):
    def test_new_evenement(self):
        convention = Convention.objects.get(numero="0001")

        convention.evenement(
            type_evenement=TypeEvenement.INSTRUCTION_AVENANT,
            description="Avenant à instruire",
        )

        self.assertEqual(1, convention.evenements.count())
        evenement = convention.evenements.first()
        self.assertEqual(evenement.type_evenement, TypeEvenement.INSTRUCTION_AVENANT)
        self.assertEqual(evenement.description, "Avenant à instruire")
        self.assertEqual(evenement.survenu_le, timezone.now())
