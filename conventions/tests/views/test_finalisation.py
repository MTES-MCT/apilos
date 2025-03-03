import pytest
from django.core.management import call_command
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from conventions.forms.convention_form_finalisation import (
    FinalisationCerfaForm,
    FinalisationNumeroForm,
)
from conventions.models.choices import ConventionStatut
from core.tests.factories import ConventionFactory
from users.tests.factories import GroupFactory, RoleFactory, UserFactory
from users.type_models import TypeRole


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "auth.json")


@pytest.fixture
def convention():
    return ConventionFactory(
        statut=ConventionStatut.INSTRUCTION.label,
        numero="1234",
        fichier_override_cerfa='{"files": {"705e2175-4a1d-4670-b9d0-de8f3c4a5432": {"uuid": "705e2175-4a1d-4670-b9d0-'
        'de8f3c4a5432", "size": 345913, "filename": "Cerfa.docx"}}, "text": ""}',
    )


@pytest.fixture
def logged_in_user(client, convention):
    user = UserFactory()
    role = RoleFactory(
        user=user,
        administration=convention.programme.administration,
        typologie=TypeRole.INSTRUCTEUR.label,
        group=GroupFactory(name="instructeur"),
    )
    client.force_login(user)

    # Définir manuellement les données de session
    session = client.session
    session["role"] = {"id": role.id}
    session.save()

    return user


@pytest.fixture
def avenant(convention):
    return ConventionFactory(
        statut=ConventionStatut.INSTRUCTION.label,
        numero="3456",
        parent_id=convention.id,
        programme=convention.programme,
        fichier_override_cerfa='{"files": {"705e2175-4a1d-4670-b9d0-de8f3c4a5432": {"uuid": "705e2175-4a1d-4670-b9d0-'
        'de8f3c4a5432", "size": 345913, "filename": "Cerfa.docx"}}, "text": ""}',
    )


@pytest.mark.django_db
def test_get_numero(client, convention, logged_in_user):
    url = reverse("conventions:finalisation_numero", args=[convention.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/numero.html")
    assert "1234" in str(response.content)
    assert (
        response.context["form_step"]["current_step"]
        == "Valider le numéro de la convention"
    )
    assert isinstance(response.context["form"], FinalisationNumeroForm)


@pytest.mark.django_db
def test_get_numero_avenant(client, avenant, logged_in_user):
    url = reverse("conventions:finalisation_numero", args=[avenant.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/numero.html")
    assert "3456" in str(response.content)
    assert (
        response.context["form_step"]["current_step"]
        == "Valider le numéro de l'avenant"
    )
    assert isinstance(response.context["form"], FinalisationNumeroForm)


@pytest.mark.django_db
def test_post_numero_fail(client, convention, logged_in_user):
    url = reverse("conventions:finalisation_numero", args=[convention.uuid])
    data = {"numero": ""}
    response = client.post(url, data)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/numero.html")
    assert "de la convention est obligatoire" in str(response.content)


@pytest.mark.django_db
def test_post_numero_success(client, convention, logged_in_user):
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
def test_get_cerfa(client, convention, logged_in_user):
    url = reverse("conventions:finalisation_cerfa", args=[convention.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/cerfa.html")
    assert response.context["form_step"]["current_step"] == "Vérifier le document CERFA"
    assert isinstance(response.context["form"], FinalisationCerfaForm)


@pytest.mark.django_db
def test_post_cerfa(client, convention, logged_in_user):
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
def test_get_validation(client, convention, logged_in_user):
    url = reverse("conventions:finalisation_validation", args=[convention.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/validation.html")
    assert (
        response.context["form_step"]["current_step"]
        == "Valider et envoyer la convention pour signature"
    )


@pytest.mark.django_db
def test_get_validation_avenant(client, avenant, logged_in_user):
    url = reverse("conventions:finalisation_validation", args=[avenant.uuid])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/finalisation/validation.html")
    assert (
        response.context["form_step"]["current_step"]
        == "Valider et envoyer l'avenant pour signature"
    )
