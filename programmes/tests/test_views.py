import copy
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse

from instructeurs.tests.factories import AdministrationFactory
from programmes.views import (
    SecondeVieExistingView,
    operation_conventions,
    seconde_vie_new,
)
from siap.siap_client.client import SIAPClient
from siap.siap_client.mock_data import operation_mock
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
@patch("programmes.views.render")
def test_operation_conventions(render_mock):
    url = reverse("programmes:operation_conventions", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation_mock

        operation_conventions(request, numero_operation="1")
        render_mock.assert_called_once()
        args, _ = render_mock.call_args
        assert args[1] == "operations/conventions.html"


@pytest.mark.django_db
def test_operation_conventions_seconde_vie_existing():
    """Test that seconde vie operations with no conventions redirect to existing.html"""
    url = reverse("programmes:operation_conventions", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = _get_seconde_vie_operation()

        response = operation_conventions(request, numero_operation="1")
        assert response.status_code == 302
        assert "operations/1/seconde_vie/existing" in response.url


@pytest.mark.django_db
@patch("programmes.views.render")
@patch("conventions.models.Convention")
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
