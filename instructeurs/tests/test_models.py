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
        expected_object_name = f"{administration.nom}"
        self.assertEqual(str(administration), expected_object_name)
        self.assertEqual(administration.label, expected_object_name)
        self.assertEqual(administration.value, administration.id)
