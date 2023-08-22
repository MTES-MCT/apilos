from datetime import date

from django.test import TestCase

from conventions.models import Convention, TypeEvenement


class EvenementModelsTest(TestCase):
    fixtures = [
        # "auth.json",
        # "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        # "users_for_tests.json",
    ]

    def test_new_evenement(self):
        convention = Convention.objects.get(numero="0002")
        convention.evenements.all().delete()

        convention.evenement(
            type_evenement=TypeEvenement.INSTRUCTION_AVENANT,
            description="Avenant à instruire",
        )

        self.assertEqual(1, convention.evenements.count())
        evenement = convention.evenements.first()
        self.assertEqual(evenement.type_evenement, TypeEvenement.INSTRUCTION_AVENANT)
        self.assertEqual(evenement.description, "Avenant à instruire")
        self.assertEqual(evenement.survenu_le, date.today())
