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
        administration = Administration.objects.get(id=1)
        expected_object_name = f"{administration.nom}"
        self.assertEqual(str(administration), expected_object_name)
