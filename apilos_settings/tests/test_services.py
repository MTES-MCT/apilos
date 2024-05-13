import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from apilos_settings.services import user_is_staff_or_admin, user_profile
from users.forms import UserNotificationForm
from users.tests.factories import UserFactory
from users.type_models import EmailPreferences


def test_user_is_staff_or_admin():

    factory = RequestFactory()

    request = factory.get("/settings/profile/")
    superuser = UserFactory.build(is_superuser=True)
    request.user = superuser

    assert user_is_staff_or_admin(request)

    staff = UserFactory.build(is_staff=True)
    request.user = staff
    assert user_is_staff_or_admin(request)

    justauser = UserFactory.build()
    request.user = justauser
    assert not user_is_staff_or_admin(request)


class TestUserProfile:
    def test_user_profile_get(self):
        factory = RequestFactory()

        request = factory.get("/settings/profile/")
        user = UserFactory.build()
        request.user = user

        response = user_profile(request)
        assert isinstance(response["form"], UserNotificationForm)
        assert response["user_is_staff_or_admin"] == user_is_staff_or_admin(request)

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
        assert response["user_is_staff_or_admin"] == user_is_staff_or_admin(request)
        assert user.preferences_email == EmailPreferences.PARTIEL

        # Check that a success message was added
        messages = list(messages)
        assert len(messages) == 1
        assert str(messages[0]) == "Votre profil a été enregistré avec succès"
