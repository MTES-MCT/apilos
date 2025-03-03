import json

import pytest
from django.test import RequestFactory

from apilos_settings.services.delegataires import DelegatairesService
from apilos_settings.services.list_services import (
    administration_list,
    bailleur_list,
    user_list,
)
from bailleurs.tests.factories import BailleurFactory
from core.tests.factories import ConventionFactory, ProgrammeFactory
from instructeurs.tests.factories import AdministrationFactory
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


@pytest.fixture
def delegataires_data():
    new_admin = AdministrationFactory(code="new_admin")
    old_admin1 = AdministrationFactory(code="old_admin1")
    old_admin2 = AdministrationFactory(code="old_admin2")

    programme1 = ProgrammeFactory(
        administration=old_admin1, code_postal="10000", ville="Troyes"
    )
    programme2 = ProgrammeFactory(
        administration=old_admin2, code_postal="10800", ville="La Vendue-Mignot"
    )
    programme3 = ProgrammeFactory(
        administration=old_admin2, code_postal="91000", ville="Evry"
    )

    convention1 = ConventionFactory(programme=programme1)
    convention2 = ConventionFactory(programme=programme2)
    convention21 = ConventionFactory(programme=programme2)
    convention3 = ConventionFactory(programme=programme3)

    return {
        "new_admin": new_admin,
        "old_admin2": old_admin2,
        "programme1": programme1,
        "programme2": programme2,
        "programme3": programme3,
        "convention1": convention1,
        "convention2": convention2,
        "convention21": convention21,
        "convention3": convention3,
    }


@pytest.mark.django_db
class TestDelegatairesService:

    def test_get_reassignation_data_communes(self, delegataires_data):
        # Create request
        communes = [
            {"code_postal": 10000, "commune": "Troyes"},
            {"code_postal": 10800, "commune": "La Vendue-Mignot"},
        ]
        request = RequestFactory().post(
            "/settings/delegataires/",
            {
                "administration": delegataires_data["new_admin"].uuid,
                "communes": json.dumps(communes),
            },
        )
        request.session = "session"
        user = UserFactory(is_staff=True)
        UserFactory()
        request.user = user

        service = DelegatairesService(request)
        data = service.get_reassignation_data()

        assert len(data.keys()) == 6
        assert data["conventions_count"] == 3
        assert data["programmes_count"] == 2
        assert data["new_admin"] == delegataires_data["new_admin"]
        assert list(data["programmes"]) == [
            delegataires_data["programme1"],
            delegataires_data["programme2"],
        ]
        assert list(data["conventions"]) == [
            delegataires_data["convention1"],
            delegataires_data["convention2"],
            delegataires_data["convention21"],
        ]
        assert list(data["old_admins"]) == [
            {"administration__code": "old_admin1", "count": 1},
            {"administration__code": "old_admin2", "count": 1},
        ]
        assert delegataires_data["convention3"] not in list(data["conventions"])

    def test_get_reassignation_data_departement(self, delegataires_data):
        # Create request
        request = RequestFactory().post(
            "/settings/delegataires/",
            {
                "administration": delegataires_data["new_admin"].uuid,
                "departement": "10",
            },
        )
        request.session = "session"
        user = UserFactory(is_staff=True)
        UserFactory()
        request.user = user

        service = DelegatairesService(request)
        data = service.get_reassignation_data()

        assert len(data.keys()) == 6
        assert data["conventions_count"] == 3
        assert data["programmes_count"] == 2
        assert data["new_admin"] == delegataires_data["new_admin"]
        assert list(data["programmes"]) == [
            delegataires_data["programme1"],
            delegataires_data["programme2"],
        ]
        assert list(data["conventions"]) == [
            delegataires_data["convention1"],
            delegataires_data["convention2"],
            delegataires_data["convention21"],
        ]
        assert list(data["old_admins"]) == [
            {"administration__code": "old_admin1", "count": 1},
            {"administration__code": "old_admin2", "count": 1},
        ]
        assert delegataires_data["convention3"] not in list(data["conventions"])

    def test_reassign(self, delegataires_data):
        # Create request
        request = RequestFactory().post(
            "/settings/delegataires/",
            {
                "administration": delegataires_data["new_admin"].uuid,
                "departement": "10",
            },
        )
        request.session = "session"
        user = UserFactory(is_staff=True)
        UserFactory()
        request.user = user

        service = DelegatairesService(request)
        data = service.get_reassignation_data()
        service.reassign(programmes=data["programmes"], new_admin=data["new_admin"])
        delegataires_data["programme1"].refresh_from_db()
        delegataires_data["programme2"].refresh_from_db()
        delegataires_data["programme3"].refresh_from_db()

        assert service.success
        assert (
            delegataires_data["programme1"].administration
            == delegataires_data["new_admin"]
        )
        assert (
            delegataires_data["programme2"].administration
            == delegataires_data["new_admin"]
        )
        assert (
            delegataires_data["programme3"].administration
            == delegataires_data["old_admin2"]
        )
