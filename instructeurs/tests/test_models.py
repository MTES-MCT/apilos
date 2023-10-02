from django.test import TestCase

from instructeurs.models import Administration


class AdministrationsModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Administration.objects.create(
            nom="CA d'Arles-Crau-Camargue-Montagnette",
            code="12345",
        )

    def test_object_str(self):
        administration = Administration.objects.get(code="12345")
        self.assertEqual(str(administration), f"{administration.nom} (12345)")
        self.assertEqual(administration.label, f"{administration.nom}")
        self.assertEqual(administration.value, administration.id)
