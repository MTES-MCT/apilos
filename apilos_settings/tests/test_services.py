import pytest
from django.test import RequestFactory

from apilos_settings.services.delegataires import DelegatairesService
from apilos_settings.services.list_services import (
    administration_list,
    bailleur_list,
    user_list,
)
from bailleurs.tests.factories import BailleurFactory
from conventions.tests.factories import ConventionFactory
from instructeurs.tests.factories import AdministrationFactory
from programmes.tests.factories import ProgrammeFactory
from users.tests.factories import UserFactory


@pytest.mark.django_db
class TestAdministrationList:

    def test_admnistration_list_superuser(self):
        AdministrationFactory()
        factory = RequestFactory()
        request = factory.get("/settings/administrations/")
        user = UserFactory(is_superuser=True)
        request.user = user

        response = administration_list(request)
        assert response["total_items"] >= 1

    def test_admnistration_list_staff(self):
        AdministrationFactory()
        factory = RequestFactory()
        request = factory.get("/settings/administrations/")
        user = UserFactory(is_staff=True)
        request.user = user

        response = administration_list(request)
        assert response["total_items"] >= 1


@pytest.mark.django_db
class TestBailleurList:

    def test_bailleur_list_superuser(self):
        BailleurFactory()
        factory = RequestFactory()
        request = factory.get("/settings/bailleurs/")
        user = UserFactory(is_superuser=True)
        request.user = user

        response = bailleur_list(request)
        assert response["total_items"] >= 1

    def test_bailleur_list_staff(self):
        BailleurFactory()
        factory = RequestFactory()
        request = factory.get("/settings/bailleurs/")
        user = UserFactory(is_staff=True)
        request.user = user

        response = bailleur_list(request)
        assert response["total_items"] >= 1


@pytest.mark.django_db
class TestUserList:

    def test_user_list_superuser(self):
        factory = RequestFactory()
        request = factory.get("/settings/users/")
        user = UserFactory(is_superuser=True)
        UserFactory()
        request.user = user

        response = user_list(request)
        assert response["total_users"] >= 1

    def test_user_list_staff(self):
        factory = RequestFactory()
        request = factory.get("/settings/users/")
        user = UserFactory(is_staff=True)
        UserFactory()
        request.user = user

        response = user_list(request)
        assert response["total_users"] >= 1


@pytest.mark.django_db
class TestDelegatairesService:

    def test_get_reassignation_data(self):
        # Create conventions
        new_admin = AdministrationFactory(code="new_admin")
        old_admin1 = AdministrationFactory(code="old_admin1")
        old_admin2 = AdministrationFactory(code="old_admin2")

        programme1 = ProgrammeFactory(
            administration=old_admin1, code_insee_departement="10"
        )
        programme2 = ProgrammeFactory(
            administration=old_admin2, code_insee_departement="10"
        )
        programme3 = ProgrammeFactory(
            administration=old_admin2, code_insee_departement="04"
        )

        convention1 = ConventionFactory(programme=programme1)
        convention2 = ConventionFactory(programme=programme2)
        convention21 = ConventionFactory(programme=programme2)
        convention3 = ConventionFactory(programme=programme3)

        # Create request and service
        request = RequestFactory().post(
            "/settings/delegataires/",
            {"administration": new_admin.uuid, "departement": "10"},
        )
        request.session = "session"
        user = UserFactory(is_staff=True)
        UserFactory()
        request.user = user
        service = DelegatairesService(request)
        service.create_form()

        data = service.get_reassignation_data()

        assert len(data.keys()) == 6
        assert data["conventions_count"] == 3
        assert data["programmes_count"] == 2
        assert data["new_admin"] == new_admin
        assert list(data["programmes"]) == [programme1, programme2]
        assert list(data["conventions"]) == [convention1, convention2, convention21]
        assert list(data["old_admins"]) == [
            {"administration__code": "old_admin1", "count": 1},
            {"administration__code": "old_admin2", "count": 1},
        ]
        assert convention3 not in list(data["conventions"])

    def test_reassign(self):
        pass
