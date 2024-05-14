import pytest
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.forms import model_to_dict
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from apilos_settings.views import EditBailleurView
from bailleurs.tests.factories import BailleurFactory
from conventions.forms.bailleur import BailleurForm
from users.tests.factories import GroupFactory, RoleFactory, UserFactory
from users.type_models import TypeRole


class SideMenuTests(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_sidemenu_is_superuser(self):
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )

        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Administrations")
        self.assertContains(response, "Bailleurs")
        self.assertContains(response, "Utilisateurs")

    def test_sidemenu_is_bailleur(self):
        client = Client()
        session = client.session
        session["bailleur"] = {"id": 1}
        session.save()

        response = client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = client.get(reverse("settings:profile"))
        self.assertContains(response, "Vos notifications")
        self.assertContains(response, "Votre entité bailleur")

    def test_sidemenu_is_instructeur(self):
        client = Client()
        session = client.session
        session["administration"] = {"id": 1}
        session.save()

        response = client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )

        response = client.get(reverse("settings:profile"))
        self.assertContains(response, "Vos notifications")
        self.assertContains(response, "Votre administration")


class TestDisplayProfile(TestCase):
    fixtures = [
        "auth.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "users_for_tests.json",
    ]

    def test_display_profile_superuser(self):
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertNotContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertContains(response, "Pas de préférences")

    def test_display_profile_instructeur(self):
        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Super Utilisateur")

    def test_display_profile_bailleur(self):
        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Super Utilisateur")


@pytest.mark.django_db
class TestEditBailleurView:
    def test_edit_bailleur_view_get(self):
        bailleur = BailleurFactory()
        url = reverse("settings:edit_bailleur", kwargs={"bailleur_uuid": bailleur.uuid})
        request = RequestFactory().get(url)
        user = UserFactory()
        RoleFactory(
            user=user,
            bailleur=bailleur,
            typologie=TypeRole.BAILLEUR,
            group=GroupFactory(),
        )
        request.user = user

        response = EditBailleurView.as_view()(request, bailleur_uuid=bailleur.uuid)

        assert response.status_code == 200
        assert isinstance(response.context_data["form"], BailleurForm)

    def test_edit_bailleur_view_post(self):
        # Setup
        bailleur = BailleurFactory()
        form_data = {
            **model_to_dict(bailleur, exclude=["parent", "operation_exceptionnelle"]),
            "nom": "nouveau nom",
            # add all other fields here
        }
        url = reverse("settings:edit_bailleur", kwargs={"bailleur_uuid": bailleur.uuid})
        user = UserFactory(is_superuser=True)
        RoleFactory(
            user=user,
            bailleur=bailleur,
            typologie=TypeRole.BAILLEUR,
            group=GroupFactory(),
        )
        request = RequestFactory().post(url, form_data)
        request.user = user

        # Mock Django messages
        request.session = "session"
        messages = FallbackStorage(request)
        request._messages = messages

        # Call the view
        response = EditBailleurView.as_view()(request, bailleur_uuid=bailleur.uuid)

        # Check the success message
        messages = list(get_messages(request))
        assert len(messages) == 1
        assert str(messages[0]) == "L'entité bailleur a été enregistrée avec succès"

        # Check the response
        assert response.status_code == 302
        assert response.url == url

        bailleur.refresh_from_db()
        assert bailleur.nom == "nouveau nom"

    def test_edit_bailleur_view_get_permission_denied(self):
        bailleur1 = BailleurFactory()
        bailleur2 = BailleurFactory()
        url = reverse(
            "settings:edit_bailleur", kwargs={"bailleur_uuid": bailleur1.uuid}
        )
        request = RequestFactory().get(url)
        user = UserFactory()
        RoleFactory(
            user=user,
            bailleur=bailleur2,
            typologie=TypeRole.BAILLEUR,
            group=GroupFactory(),
        )
        request.user = user

        with pytest.raises(PermissionDenied):
            EditBailleurView.as_view()(request, bailleur_uuid=bailleur1.uuid)

    def test_edit_bailleur_view_post_permission_denied(self):
        bailleur1 = BailleurFactory()
        bailleur2 = BailleurFactory()
        url = reverse(
            "settings:edit_bailleur", kwargs={"bailleur_uuid": bailleur1.uuid}
        )
        request = RequestFactory().post(url)
        user = UserFactory()
        RoleFactory(
            user=user,
            bailleur=bailleur2,
            typologie=TypeRole.BAILLEUR,
            group=GroupFactory(),
        )
        request.user = user

        with pytest.raises(PermissionDenied):
            EditBailleurView.as_view()(request, bailleur_uuid=bailleur1.uuid)
