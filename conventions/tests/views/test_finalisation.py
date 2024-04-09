import pytest
from django.conf import settings
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from waffle.testutils import override_flag

from conventions.models.choices import ConventionStatut
from conventions.tests.factories import ConventionFactory


@pytest.fixture
def convention():
    return ConventionFactory(
        statut=ConventionStatut.INSTRUCTION.label,
        numero="1234",
        fichier_override_cerfa='{"files": {"705e2175-4a1d-4670-b9d0-de8f3c4a5432": {"uuid": "705e2175-4a1d-4670-b9d0-'
        'de8f3c4a5432", "size": 345913, "filename": "Cerfa.docx"}}, "text": ""}',
    )


@pytest.mark.django_db
@override_flag(settings.FLAG_OVERRIDE_CERFA, active=True)
def test_get_numero(client, convention):
    url = reverse("conventions:finalisation_numero", args=[convention.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/numero.html")
    assert "1234" in str(response.content)


@pytest.mark.django_db
@override_flag(settings.FLAG_OVERRIDE_CERFA, active=True)
def test_post_numero_fail(client, convention):
    url = reverse("conventions:finalisation_numero", args=[convention.uuid])
    data = {"numero": ""}
    response = client.post(url, data)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/numero.html")
    assert "de la convention est obligatoire" in str(response.content)


@pytest.mark.django_db
@override_flag(settings.FLAG_OVERRIDE_CERFA, active=True)
def test_post_numero_success(client, convention):
    url = reverse("conventions:finalisation_numero", args=[convention.uuid])
    data = {"numero": "1234567"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response["Location"] == reverse(
        "conventions:finalisation_cerfa", args=[convention.uuid]
    )
    convention.refresh_from_db()
    assert convention.numero == "1234567"


@pytest.mark.django_db
@override_flag(settings.FLAG_OVERRIDE_CERFA, active=True)
def test_get_cerfa(client, convention):
    url = reverse("conventions:finalisation_cerfa", args=[convention.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/cerfa.html")
    assert "Cerfa.docx" in str(response.content)


@pytest.mark.django_db
@override_flag(settings.FLAG_OVERRIDE_CERFA, active=True)
def test_post_cerfa(client, convention):
    url = reverse("conventions:finalisation_cerfa", args=[convention.uuid])
    data = {}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response["Location"] == reverse(
        "conventions:finalisation_validation", args=[convention.uuid]
    )
    convention.refresh_from_db()
    assert convention.fichier_override_cerfa == '{"files": {}, "text": ""}'


@pytest.mark.django_db
@override_flag(settings.FLAG_OVERRIDE_CERFA, active=True)
def test_get_validation(client, convention):
    url = reverse("conventions:finalisation_validation", args=[convention.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/validation.html")
