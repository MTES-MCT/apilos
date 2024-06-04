from unittest.mock import patch

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse

from instructeurs.tests.factories import AdministrationFactory
from programmes.views import SecondeVieExistingView, SecondeVieNewView
from siap.siap_client.client import SIAPClient
from siap.siap_client.mock_data import operation_mock
from users.tests.factories import GroupFactory, RoleFactory, UserFactory
from users.type_models import TypeRole


def get_habilited_request(url):
    user = UserFactory()
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


@pytest.mark.django_db
def test_seconde_vie_new_view():

    url = reverse("programmes:seconde_vie_new", kwargs={"numero_operation": "1"})
    request = get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation_mock

        response = SecondeVieNewView.as_view()(request, numero_operation="1").render()
        assert response.status_code == 200
        assert b"Seconde Vie - Nouvelles conventions" in response.content


@pytest.mark.django_db
def test_seconde_vie_existing_view():

    url = reverse("programmes:seconde_vie_existing", kwargs={"numero_operation": "1"})
    request = get_habilited_request(url)

    with patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_instance = mock_get_instance.return_value
        mock_instance.get_operation.return_value = operation_mock

        response = SecondeVieExistingView.as_view()(
            request, numero_operation="1"
        ).render()
        assert response.status_code == 200
        assert b"Seconde Vie - Conventions existantes" in response.content
