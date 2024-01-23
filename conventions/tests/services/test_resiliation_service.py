from datetime import date

from django.test import RequestFactory, TestCase

from conventions.services.resiliation import (
    ConventionResiliationActeService,
    ConventionResiliationService,
)
from conventions.tests.factories import ConventionFactory
from users.models import User


class ConventionResiliationActeServiceTest(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        user = User.objects.get(username="nicolas")
        request = RequestFactory().post(
            "/",
            data={
                "date_resiliation_definitive": "2022-09-03",
                "fichier_instruction_resiliation": "test_file",
            },
        )
        request.user = user
        self.service = ConventionResiliationActeService(
            convention=ConventionFactory(),
            request=request,
        )

    def test_get(self):
        self.service.get()

        assert set(self.service.form.initial.keys()) == {
            "uuid",
            "date_resiliation_definitive",
            "fichier_instruction_resiliation",
            "fichier_instruction_resiliation_files",
        }

    def test_save(self):
        self.service.save()
        self.service.convention.refresh_from_db()

        assert self.service.convention.date_resiliation_definitive == date(2022, 9, 3)
        assert "test_file" in self.service.convention.fichier_instruction_resiliation


class ConventionResiliationServiceTest(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        user = User.objects.get(username="nicolas")
        request = RequestFactory().post(
            "/",
            data={
                "date_resiliation_demandee": "2022-09-04",
                "motif_resiliation": "Motif de résiliation",
                "champ_libre_avenant": "Champ libre avenant",
            },
        )
        request.user = user
        self.service = ConventionResiliationService(
            convention=ConventionFactory(),
            request=request,
        )

    def test_get(self):
        self.service.get()

        assert set(self.service.form.initial.keys()) == {
            "uuid",
            "date_resiliation_demandee",
            "motif_resiliation",
            "champ_libre_avenant",
        }

    def test_save(self):
        self.service.save()
        self.service.convention.refresh_from_db()

        assert self.service.convention.date_resiliation_demandee == date(2022, 9, 4)
        assert self.service.convention.motif_resiliation == "Motif de résiliation"
        assert self.service.convention.champ_libre_avenant == "Champ libre avenant"
