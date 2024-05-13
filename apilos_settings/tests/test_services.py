import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.forms import model_to_dict
from django.test import RequestFactory

from apilos_settings.services import (
    administration_list,
    bailleur_list,
    edit_administration,
    user_list,
    user_profile,
)
from bailleurs.tests.factories import BailleurFactory
from instructeurs.forms import AdministrationForm
from instructeurs.tests.factories import AdministrationFactory
from users.forms import UserNotificationForm
from users.tests.factories import UserFactory
from users.type_models import EmailPreferences


class TestUserProfile:
    def test_user_profile_get(self):
        factory = RequestFactory()

        request = factory.get("/settings/profile/")
        user = UserFactory.build()
        request.user = user

        response = user_profile(request)
        assert isinstance(response["form"], UserNotificationForm)

    @pytest.mark.django_db
    def test_user_profile_post(self):
        factory = RequestFactory()

        request = factory.post(
            "/settings/profile/", {"preferences_email": EmailPreferences.PARTIEL}
        )
        user = UserFactory.create()
        request.user = user

        # Mock Django messages
        request.session = "session"
        messages = FallbackStorage(request)
        request._messages = messages

        response = user_profile(request)
        assert isinstance(response["form"], UserNotificationForm)
        assert user.preferences_email == EmailPreferences.PARTIEL

        # Check that a success message was added
        messages = list(messages)
        assert len(messages) == 1
        assert str(messages[0]) == "Votre profil a été enregistré avec succès"


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


@pytest.mark.django_db
class TestEditAdministration:

    def test_edit_administration_get(self):
        factory = RequestFactory()
        administration = AdministrationFactory()
        request = factory.get(f"/settings/administrations/{administration.uuid}/")
        user = UserFactory(is_superuser=True)
        request.user = user

        response = edit_administration(request, administration.uuid)
        assert isinstance(response["form"], AdministrationForm)

    def test_edit_administration_post(self):
        factory = RequestFactory()
        administration = AdministrationFactory()
        request = factory.post(
            f"/settings/administrations/{administration.uuid}/",
            {
                **model_to_dict(
                    administration,
                    exclude=["code_dans_galion", "signataire_bloc_signature"],
                ),
                "nom": "nouveau nom",
            },
        )
        user = UserFactory(is_superuser=True)
        request.user = user

        # Mock Django messages
        request.session = "session"
        messages = FallbackStorage(request)
        request._messages = messages

        response = edit_administration(request, administration.uuid)
        assert isinstance(response["form"], AdministrationForm)

        administration.refresh_from_db()

        assert administration.nom == "nouveau nom"
