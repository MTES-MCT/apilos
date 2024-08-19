import copy
from unittest.mock import patch

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
@patch("programmes.views.render")
def test_operation_conventions_seconde_vie_choice(render_mock):
    url = reverse("programmes:operation_conventions", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = _get_seconde_vie_operation()

        operation_conventions(request, numero_operation="1")
        render_mock.assert_called_once()
        args, _ = render_mock.call_args
        assert args[1] == "operations/seconde_vie/choice.html"


@pytest.mark.django_db
@patch("programmes.views.render")
def test_operation_conventions_seconde_vie_create_conventions(render_mock):

    url = reverse("programmes:seconde_vie_new", kwargs={"numero_operation": "1"})
    request = _get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = _get_seconde_vie_operation()

        seconde_vie_new(request, numero_operation="1")
        render_mock.assert_called_once()
        args, _ = render_mock.call_args
        assert args[1] == "operations/conventions.html"
        assert args[2]["conventions"].object_list.count() == 1

        # Get operation : display the created convention instead of choice.html
        url = reverse(
            "programmes:operation_conventions", kwargs={"numero_operation": "1"}
        )
        request = _get_habilited_request(url)

        operation_conventions(request, numero_operation="1")
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

        response = SecondeVieExistingView.as_view()(
            request, numero_operation="1"
        ).render()
        assert response.status_code == 200
        assert b"Seconde Vie - Conventions existantes" in response.content
