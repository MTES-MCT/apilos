from datetime import date

import pytest
from django.test import RequestFactory

from conventions.services.resiliation import (
    ConventionResiliationActeService,
    ConventionResiliationService,
)
from core.tests.factories import ConventionFactory
from users.tests.factories import UserFactory


@pytest.fixture()
def resiliation_acte_service():
    user = UserFactory(is_superuser=True)
    request = RequestFactory().post(
        "/",
        data={
            "fichier_instruction_resiliation": "test_file",
        },
    )
    request.user = user
    return ConventionResiliationActeService(
        convention=ConventionFactory(),
        request=request,
    )


@pytest.mark.django_db
class TestConventionResiliationActeService:
    def test_get(self, resiliation_acte_service):
        resiliation_acte_service.get()

        assert set(resiliation_acte_service.form.initial.keys()) == {
            "uuid",
            "fichier_instruction_resiliation",
            "fichier_instruction_resiliation_files",
        }

    def test_save(self, resiliation_acte_service):
        resiliation_acte_service.save()
        resiliation_acte_service.convention.refresh_from_db()

        assert (
            "test_file"
            in resiliation_acte_service.convention.fichier_instruction_resiliation
        )


@pytest.fixture()
def resiliation_service():
    user = UserFactory(is_superuser=True)
    request = RequestFactory().post(
        "/",
        data={
            "date_resiliation": "2022-09-04",
            "motif_resiliation": "Motif de résiliation",
            "commentaires": "Commentaires test",
        },
    )
    request.user = user
    return ConventionResiliationService(
        convention=ConventionFactory(),
        request=request,
    )


@pytest.mark.django_db
class TestConventionResiliationService:
    def test_get(self, resiliation_service):
        resiliation_service.get()

        assert set(resiliation_service.form.initial.keys()) == {
            "uuid",
            "date_resiliation",
            "motif_resiliation",
            "commentaires",
            "commentaires_files",
        }

    def test_save(self, resiliation_service):
        resiliation_service.save()
        resiliation_service.convention.refresh_from_db()

        assert resiliation_service.convention.date_resiliation == date(2022, 9, 4)
        assert (
            resiliation_service.convention.motif_resiliation == "Motif de résiliation"
        )
        assert (
            resiliation_service.convention.commentaires
            == '{"files": [], "text": "Commentaires test"}'
        )
