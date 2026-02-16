import copy
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from conventions.models import Convention, ConventionGroupingError
from core.tests.factories import ConventionFactory, ProgrammeFactory
from instructeurs.tests.factories import AdministrationFactory
from programmes.views import (
    SecondeVieExistingView,
    operation_conventions,
    seconde_vie_new,
)
from siap.siap_client.client import SIAPClient
from siap.siap_client.mock_data import operation_mock
from users.models import User
from users.tests.factories import GroupFactory, RoleFactory, UserFactory
from users.type_models import TypeRole


def _get_habilited_request(url):
    user = UserFactory()
    user.cerbere_login = True
    administration = AdministrationFactory()
    RoleFactory(
        user=user,
        administration=administration,
        typologie=TypeRole.INSTRUCTEUR,
        group=GroupFactory(),
    )

    request = RequestFactory().get(url)
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session["habilitation_id"] = "1"
    request.session.save()
    request.user = user
    return request


def _get_seconde_vie_operation():
    operation_seconde_vie = copy.deepcopy(operation_mock)
    operation_seconde_vie["donneesOperation"]["aides"] = [{"code": "SECD_VIE"}]
    return operation_seconde_vie


@pytest.mark.django_db
@mock.patch("programmes.views.render")
def test_operation_conventions(render_mock):
    url = reverse("programmes:operation_conventions", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation_mock

        operation_conventions(request, numero_operation="1")
        render_mock.assert_called_once()
        args, _ = render_mock.call_args
        assert args[1] == "operations/conventions.html"


@pytest.mark.django_db
def test_operation_conventions_seconde_vie_existing():
    url = reverse("programmes:operation_conventions", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = _get_seconde_vie_operation()

        response = operation_conventions(request, numero_operation="1")
        assert response.status_code == 302
        assert "operations/1/seconde_vie/existing" in response.url


@pytest.mark.django_db
@mock.patch("programmes.views.render")
@mock.patch("conventions.models.Convention")
def test_operation_conventions_seconde_vie_create_conventions(
    mock_convention_model, render_mock
):
    new_conventions_qs = MagicMock()
    new_conventions_qs.count.return_value = 0
    new_conventions_qs.order_by.return_value = new_conventions_qs
    mock_convention_model.objects.filter.return_value = new_conventions_qs

    url = reverse("programmes:seconde_vie_new", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        get_operation_return_value = _get_seconde_vie_operation()
        mock_instance.get_operation.return_value = get_operation_return_value
        numero_operation = get_operation_return_value["donneesOperation"][
            "numeroOperation"
        ]

        seconde_vie_new(request, numero_operation=numero_operation)
        render_mock.assert_called_once()
        args, _ = render_mock.call_args
        assert args[1] == "operations/conventions.html"
        assert args[2]["conventions"].object_list.count() == 1

        # Get operation : display the created convention instead of choice.html
        url = reverse(
            "programmes:operation_conventions",
            kwargs={"numero_operation": numero_operation},
        )
        request = _get_habilited_request(url)

        operation_conventions(request, numero_operation=numero_operation)
        render_mock.assert_called()
        args, _ = render_mock.call_args

        assert args[1] == "operations/conventions.html"
        assert args[2]["conventions"].object_list.count() == 1


@pytest.mark.django_db
def test_seconde_vie_existing_view():

    url = reverse("programmes:seconde_vie_existing", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation_mock

        response = SecondeVieExistingView.as_view()(request, numero_operation="1")
        assert response.status_code == 200
        assert b"Seconde Vie - Conventions existantes" in response.content


@pytest.mark.django_db
@mock.patch("programmes.views.render")
def test_operation_conventions_no_programmes(render_mock):
    numero_operation = "1"
    url = reverse(
        "programmes:operation_conventions",
        kwargs={"numero_operation": numero_operation},
    )
    request = _get_habilited_request(url)
    message_middleware = MessageMiddleware(lambda x: None)
    message_middleware.process_request(request)

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = None

        response = operation_conventions(request, numero_operation=numero_operation)

        assert response.status_code == 302

        expected_url = (
            reverse("conventions:search") + f"?search_numero={numero_operation}"
        )
        assert response.url == expected_url

        storage = get_messages(request)
        message_list = [m.message for m in storage]
        assert "Aucun programme trouvé" in " ".join(message_list)


@pytest.mark.django_db
def test_seconde_vie_new_with_multiple_conventions():
    numero_operation = "20220600006"
    url = reverse(
        "programmes:seconde_vie_new", kwargs={"numero_operation": numero_operation}
    )
    request = _get_habilited_request(url)

    programme = ProgrammeFactory(numero_operation=numero_operation, seconde_vie=True)
    operation = _get_seconde_vie_operation()
    operation["donneesOperation"]["numeroOperation"] = numero_operation

    conv_1 = ConventionFactory(programme=programme, statut="1. Projet", parent=None)
    conv_2 = ConventionFactory(programme=programme, statut="1. Projet", parent=None)

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation

        with mock.patch(
            "programmes.services.get_or_create_conventions_from_siap",
            return_value=(programme, [], [conv_1, conv_2]),
        ):
            with mock.patch(
                "conventions.models.Convention.objects.group_conventions"
            ) as mock_group:
                mock_group.side_effect = ConventionGroupingError("Error")

                response = seconde_vie_new(request, numero_operation=numero_operation)

                assert response.status_code == 302
                assert "/conventions/bailleur/" in response.url
                mock_group.assert_called_once()


@pytest.mark.django_db
def test_seconde_vie_new_with_successful_convention_grouping():
    numero_operation = "20220600007"
    url = reverse(
        "programmes:seconde_vie_new", kwargs={"numero_operation": numero_operation}
    )
    request = _get_habilited_request(url)

    programme = ProgrammeFactory(numero_operation=numero_operation, seconde_vie=True)
    initial_convention_count = programme.conventions.count()
    operation = _get_seconde_vie_operation()
    operation["donneesOperation"]["numeroOperation"] = numero_operation

    conv_1 = ConventionFactory(programme=programme, statut="1. Projet", parent=None)
    conv_2 = ConventionFactory(programme=programme, statut="1. Projet", parent=None)
    grouped_convention_result = ConventionFactory(
        programme=programme, statut="2. Signé", parent=None, numero="GROUPED"
    )

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation

        with mock.patch(
            "programmes.services.get_or_create_conventions_from_siap",
            return_value=(programme, [], [conv_1, conv_2]),
        ):
            with mock.patch(
                "conventions.models.Convention.objects.group_conventions"
            ) as mock_group:
                mock_group.return_value = (programme, [], grouped_convention_result)

                response = seconde_vie_new(request, numero_operation=numero_operation)

                assert (
                    response.status_code == 302
                ), f"Expected 302 redirect, got {response.status_code}"

                assert (
                    str(grouped_convention_result.uuid) in response.url
                ), f"Grouped convention UUID {grouped_convention_result.uuid} not in redirect URL {response.url}"

                assert (
                    mock_group.call_count == 1
                ), f"Expected group_conventions to be called once, was called {mock_group.call_count} times"

                called_uuids = mock_group.call_args[0][0]
                assert (
                    len(called_uuids) == 2
                ), f"Expected 2 convention UUIDs to be grouped, got {len(called_uuids)}"

                current_convention_count = programme.conventions.count()
                expected_total = initial_convention_count + 3  # 2 created + 1 grouped
                assert current_convention_count == expected_total, (
                    f"Expected {expected_total} total conventions, got {current_convention_count}. "
                    "This ensures conventions were actually created in the database."
                )

                assert grouped_convention_result.programme_id == programme.id, (
                    f"Grouped convention doesn't belong to expected programme {programme.id}. "
                    "The result of grouping should preserve the programme association."
                )

                assert (
                    grouped_convention_result.numero == "GROUPED"
                ), f"Grouped convention numero should be 'GROUPED', got '{grouped_convention_result.numero}'"
                assert (
                    grouped_convention_result.statut == "2. Signé"
                ), f"Grouped convention status should be '2. Signé', got '{grouped_convention_result.statut}'"


class SecondeVieConventionGroupingTests(TestCase):

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

    def setUp(self):

        self.factory = RequestFactory()

        self.programme = ProgrammeFactory(
            numero_operation="20220600100",
            seconde_vie=True,
            administration=AdministrationFactory(code="admin_sv"),
            code_postal="75000",
            ville="Paris",
        )

        self.convention_1 = ConventionFactory(
            programme=self.programme,
            numero="SV0001",
            statut="1. Projet",
            parent=None,
        )
        self.convention_2 = ConventionFactory(
            programme=self.programme,
            numero="SV0002",
            statut="1. Projet",
            parent=None,
        )

        self.user = User.objects.get(username="raph")
        self.Convention = Convention

    def _get_seconde_vie_operation_mock(self):
        operation = copy.deepcopy(operation_mock)
        operation["donneesOperation"]["aides"] = [{"code": "SECD_VIE"}]
        operation["donneesOperation"]["numeroOperation"] = "20220600100"
        return operation

    @mock.patch.object(SIAPClient, "get_instance")
    def test_grouping_conventions_exist(self, mock_siap):
        mock_instance = mock_siap.return_value
        mock_instance.get_operation.return_value = (
            self._get_seconde_vie_operation_mock()
        )

        request = self.factory.post(
            reverse(
                "programmes:seconde_vie_new", kwargs={"numero_operation": "20220600100"}
            )
        )
        request.user = self.user
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        conventions = list(self.programme.conventions.filter(parent__isnull=True))
        self.assertEqual(len(conventions), 2)

        for convention in conventions:
            self.assertEqual(convention.statut, "1. Projet")

    @mock.patch.object(SIAPClient, "get_instance")
    def test_seconde_vie_operation_has_secd_vie_code(self, mock_siap):
        """Test that seconde vie operations have SECD_VIE code"""
        mock_instance = mock_siap.return_value
        mock_instance.get_operation.return_value = (
            self._get_seconde_vie_operation_mock()
        )

        operation = self._get_seconde_vie_operation_mock()
        aides = operation["donneesOperation"]["aides"]
        aide_codes = [aide["code"] for aide in aides]
        self.assertIn("SECD_VIE", aide_codes)


@pytest.mark.django_db
def test_seconde_vie_existing_view_with_ajax():
    url = reverse("programmes:seconde_vie_existing", kwargs={"numero_operation": "1"})
    user = UserFactory()
    user.cerbere_login = True
    administration = AdministrationFactory()
    RoleFactory(
        user=user,
        administration=administration,
        typologie=TypeRole.INSTRUCTEUR,
        group=GroupFactory(),
    )

    request = RequestFactory().get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session["habilitation_id"] = "1"
    request.session.save()
    request.user = user

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation_mock

        response = SecondeVieExistingView.as_view()(request, numero_operation="1")
        assert response.status_code == 200
        assert b"_search_results.html" in response.content or response.content
