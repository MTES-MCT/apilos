import pytest
from django.test import RequestFactory

from apilos_settings.services import administration_list, bailleur_list, user_list
from bailleurs.tests.factories import BailleurFactory
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
        assert response["administrations"].paginator.count >= 1

    def test_admnistration_list_staff(self):
        AdministrationFactory()
        factory = RequestFactory()
        request = factory.get("/settings/administrations/")
        user = UserFactory(is_staff=True)
        request.user = user

        response = administration_list(request)
        assert response["administrations"].paginator.count >= 1


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
