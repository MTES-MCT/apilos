from datetime import date

from bs4 import BeautifulSoup
from django.conf import settings
from django.http.request import HttpRequest
from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from conventions.models import ConventionStatut
from conventions.services.search import UserConventionSearchService
from conventions.tests.factories import ConventionFactory
from conventions.views.conventions import (
    ConventionTabSearchBaseView,
    ConventionTabsMixin,
)
from users.models import User


class ConventionIndexViewTests(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def _login(self):
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

    def test_get_index(self):
        self._login()

        with override_flag(settings.FLAG_NEW_SEARCH, active=True):
            response = self.client.get(reverse("conventions:index"))
            self.assertRedirects(response, reverse("conventions:search"))

        with override_flag(settings.FLAG_NEW_SEARCH, active=False):
            response = self.client.get(reverse("conventions:index"))
            self.assertRedirects(response, reverse("conventions:search_instruction"))

    def test_get_list_active(self):
        """
        Test displaying convention list as superuser without filter nor order
        """
        self._login()

        response = self.client.get(reverse("conventions:search_instruction"))
        soup = BeautifulSoup(response.content, "html.parser")
        galion_refs = soup.find_all(attrs={"data-test-role": "programme-galion-cell"})
        financements = soup.find_all(
            attrs={"data-test-role": "programme-financement-cell"}
        )

        self.assertEqual(len(galion_refs), 4)
        self.assertEqual(len(financements), 4)
        self.assertEqual(
            {r.text.strip() for r in galion_refs}, {"Op. : 12345", "Op. : 98765"}
        )
        self.assertEqual({f.text.strip() for f in financements}, {"PLAI", "PLUS"})

    def test_get_list_active_ordered_by_bailleur(self):
        """
        Test displaying convention list as superuser without filter but with bailleur order
        """
        self._login()

        response = self.client.get(
            reverse("conventions:search_instruction"),
            data={"order_by": "programme__bailleur__nom"},
        )
        soup = BeautifulSoup(response.content, "html.parser")
        galion_refs = soup.find_all(attrs={"data-test-role": "programme-galion-cell"})
        financements = soup.find_all(
            attrs={"data-test-role": "programme-financement-cell"}
        )

        self.assertEqual(
            {r.text.strip() for r in galion_refs}, {"Op. : 12345", "Op. : 98765"}
        )
        self.assertEqual({f.text.strip() for f in financements}, {"PLUS", "PLAI"})

    def test_get_tabs_basic(self):
        class DummyClassWithTabs(ConventionTabsMixin):
            def __init__(self):
                self.request = HttpRequest()
                self.request.user = User.objects.get(username="nicolas")

        self.assertEqual(len(DummyClassWithTabs().get_tabs()), 3)

    def test_get_tabs_with_new_view(self):
        class DummyClassWithTabs(ConventionTabsMixin):
            def __init__(self):
                self.request = HttpRequest()
                self.request.user = User.objects.get(username="nicolas")

        class DummyService(UserConventionSearchService):
            weight = 1000000
            verbose_name = "Je suis un service"

        class DummyConventionView(ConventionTabSearchBaseView):
            name = "search_instruction"
            service_class = DummyService

        tabs = DummyClassWithTabs().get_tabs()

        self.assertEqual(len(tabs), 4)
        self.assertEqual(tabs[-1]["title"], "Je suis un service")


class ConventionIndexFiltersViewTests(TestCase):
    fixtures = [
        "auth.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "users_for_tests.json",
    ]

    def test_filter_date_validation(self):
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        ConventionFactory(
            statut=ConventionStatut.SIGNEE.label,
            televersement_convention_signee_le="2023-01-01",
        )
        ConventionFactory(
            statut=ConventionStatut.SIGNEE.label,
            televersement_convention_signee_le="2020-01-01",
        )

        response = self.client.get(
            reverse("conventions:search_active"), data={"date_signature": "2000"}
        )
        self.assertEqual(
            response.context["date_signature_choices"],
            sorted([str(d) for d in range(2020, date.today().year + 1)], reverse=True),
        )
        self.assertEqual(response.context["filtered_conventions_count"], 0)

        response = self.client.get(
            reverse("conventions:search_active"), data={"date_signature": "2023"}
        )
        self.assertEqual(response.context["filtered_conventions_count"], 1)
