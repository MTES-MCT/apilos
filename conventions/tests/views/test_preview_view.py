import io
from unittest.mock import patch
from uuid import UUID

import pytest
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from conventions.models.choices import ConventionStatut
from core.tests.factories import ConventionFactory
from ecoloweb.models import EcoloReference
from users.tests.factories import GroupFactory, RoleFactory, UserFactory
from users.type_models import TypeRole


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "auth.json")


@pytest.fixture
def convention():
    return ConventionFactory(uuid=UUID("00000000-0000-0000-0000-000000000000"))


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

    session = client.session
    session["role"] = {"id": role.id}
    session.save()

    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "statut, expected_template, expected_content",
    [
        (ConventionStatut.SIGNEE.label, "test-signed-file.pdf", b"Test PDF signes"),
        (ConventionStatut.RESILIEE.label, "test-signed-file.pdf", b"Test PDF signes"),
        (ConventionStatut.DENONCEE.label, "test-signed-file.pdf", b"Test PDF signes"),
        (ConventionStatut.ANNULEE.label, "test-signed-file.pdf", b"Test PDF signes"),
        (
            ConventionStatut.INSTRUCTION.label,
            "00000000-0000-0000-0000-000000000000.pdf",
            b"Test PDF en instruction",
        ),
        (
            ConventionStatut.CORRECTION.label,
            "00000000-0000-0000-0000-000000000000.pdf",
            b"Test PDF en instruction",
        ),
        (
            ConventionStatut.A_SIGNER.label,
            "test-signed-file.pdf",
            b"Test PDF signes",
        ),
    ],
)
def test_display_pdf(
    client, convention, logged_in_user, statut, expected_template, expected_content
):
    convention.statut = statut
    convention.nom_fichier_signe = "test-signed-file.pdf"
    convention.save()

    convention_path = "conventions/00000000-0000-0000-0000-000000000000/convention_docs"
    default_storage.save(
        f"{convention_path}/{convention.nom_fichier_signe}",
        io.BytesIO(b"Test PDF signes"),
    )
    default_storage.save(
        f"{convention_path}/00000000-0000-0000-0000-000000000000.pdf",
        io.BytesIO(b"Test PDF en instruction"),
    )

    url = reverse("conventions:display_pdf", args=[convention.uuid])
    response = client.get(url)

    assert response.status_code == 200
    assert f'inline; filename="{expected_template}"' in response["Content-Disposition"]
    content = b"".join(response.streaming_content)
    assert content == expected_content

    default_storage.delete(f"{convention_path}/{convention.nom_fichier_signe}")
    default_storage.delete(f"{convention_path}/00000000-0000-0000-000000000000.pdf")


@pytest.mark.django_db
def test_display_pdf_a_signer(client, convention, logged_in_user):
    # Case where nom_fichier_signe is not defined
    convention.statut = ConventionStatut.A_SIGNER.label
    convention.save()

    convention_path = "conventions/00000000-0000-0000-0000-000000000000/convention_docs"
    default_storage.save(
        f"{convention_path}/00000000-0000-0000-0000-000000000000.pdf",
        io.BytesIO(b"Test PDF en instruction"),
    )

    url = reverse("conventions:display_pdf", args=[convention.uuid])
    response = client.get(url)

    assert response.status_code == 200
    assert (
        'inline; filename="00000000-0000-0000-0000-000000000000.pdf"'
        in response["Content-Disposition"]
    )
    content = b"".join(response.streaming_content)
    assert content == b"Test PDF en instruction"

    default_storage.delete(f"{convention_path}/00000000-0000-0000-000000000000.pdf")


@pytest.mark.django_db
def test_display_pdf_fallback(client, convention, logged_in_user):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000001")
    convention.statut = ConventionStatut.INSTRUCTION.label
    convention.save()

    convention_path = "conventions/00000000-0000-0000-0000-000000000001/convention_docs"
    default_storage.save(
        f"{convention_path}/00000000-0000-0000-0000-000000000001.docx",
        io.BytesIO(b"Test DOCX"),
    )

    url = reverse("conventions:display_pdf", args=[convention.uuid])
    response = client.get(url)

    assert response.status_code == 200
    assert (
        'inline; filename="00000000-0000-0000-0000-000000000001.docx"'
        in response["Content-Disposition"]
    )
    content = b"".join(response.streaming_content)
    assert content == b"Test DOCX"

    default_storage.save(
        f"{convention_path}/00000000-0000-0000-0000-000000000001.pdf",
        io.BytesIO(b"Test PDF"),
    )

    url = reverse("conventions:display_pdf", args=[convention.uuid])
    response = client.get(url)

    assert response.status_code == 200
    assert (
        'inline; filename="00000000-0000-0000-0000-000000000001.pdf"'
        in response["Content-Disposition"]
    )
    content = b"".join(response.streaming_content)
    assert content == b"Test PDF"

    default_storage.delete(
        f"{convention_path}/00000000-0000-0000-0000-000000000001.pdf"
    )
    default_storage.delete(
        f"{convention_path}/00000000-0000-0000-0000-000000000001.docx"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "statut",
    [
        (ConventionStatut.SIGNEE.label),
        (ConventionStatut.RESILIEE.label),
        (ConventionStatut.DENONCEE.label),
        (ConventionStatut.ANNULEE.label),
        (ConventionStatut.INSTRUCTION.label),
        (ConventionStatut.CORRECTION.label),
        (ConventionStatut.A_SIGNER.label),
    ],
)
def test_display_pdf_no_file(client, convention, logged_in_user, statut):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000002")
    convention.statut = statut
    convention.nom_fichier_signe = ""
    convention.save()

    url = reverse("conventions:display_pdf", args=[convention.uuid])
    response = client.get(url)

    assert response.status_code == 200
    assertTemplateUsed(response, "conventions/no_convention_document.html")
    assert "en cours de génération" in response.content.decode()


@pytest.mark.django_db
def test_display_pdf_no_file_ecolo(client, convention, logged_in_user):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000003")
    convention.nom_fichier_signe = ""
    convention.save()
    EcoloReference.objects.create(
        apilos_model="conventions.Convention",
        apilos_id=convention.id,
        ecolo_id="123",
        departement="13",
    )

    url = reverse("conventions:display_pdf", args=[convention.uuid])
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "La convention n'existe pas dans Apilos" in content
    assert "en cours de génération" not in content


@pytest.mark.django_db
def test_preview_shows_regenerate_button_when_document_missing(
    client, convention, logged_in_user
):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000004")
    convention.statut = ConventionStatut.A_SIGNER.label
    convention.nom_fichier_signe = ""
    convention.save()

    response = client.get(reverse("conventions:preview", args=[convention.uuid]))

    assert response.status_code == 200
    assert response.context["can_regenerate_document"] is True
    assert "regenerate_document_button" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "statut",
    [
        ConventionStatut.INSTRUCTION.label,
        ConventionStatut.CORRECTION.label,
        ConventionStatut.SIGNEE.label,
    ],
)
def test_preview_hides_regenerate_button_when_not_a_signer(
    client, convention, logged_in_user, statut
):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000005")
    convention.statut = statut
    convention.nom_fichier_signe = ""
    convention.save()

    response = client.get(reverse("conventions:preview", args=[convention.uuid]))

    assert response.status_code == 200
    assert response.context["can_regenerate_document"] is False
    assert "regenerate_document_button" not in response.content.decode()


@pytest.mark.django_db
def test_preview_hides_regenerate_button_when_document_exists(
    client, convention, logged_in_user
):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000006")
    convention.statut = ConventionStatut.A_SIGNER.label
    convention.nom_fichier_signe = ""
    convention.save()

    pdf_path = (
        "conventions/00000000-0000-0000-0000-000000000006/convention_docs/"
        "00000000-0000-0000-0000-000000000006.pdf"
    )
    default_storage.save(pdf_path, io.BytesIO(b"Test PDF"))

    response = client.get(reverse("conventions:preview", args=[convention.uuid]))

    assert response.status_code == 200
    assert response.context["can_regenerate_document"] is False

    default_storage.delete(pdf_path)


@pytest.mark.django_db
@patch("conventions.views.conventions.task_generate_and_send.delay")
def test_regenerate_document_triggers_task(
    mock_delay, client, convention, logged_in_user
):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000007")
    convention.statut = ConventionStatut.A_SIGNER.label
    convention.nom_fichier_signe = ""
    convention.save()

    response = client.post(
        reverse("conventions:regenerate_document", args=[convention.uuid])
    )

    assert response.status_code == 302
    assert response.url == reverse("conventions:preview", args=[convention.uuid])
    mock_delay.assert_called_once()
    kwargs = mock_delay.call_args.kwargs
    assert kwargs["convention_uuid"] == str(convention.uuid)
    assert kwargs["convention_url"].endswith(
        reverse("conventions:preview", args=[convention.uuid])
    )
    assert kwargs["convention_email_validator"] == logged_in_user.email


@pytest.mark.django_db
@patch("conventions.views.conventions.task_generate_and_send.delay")
def test_regenerate_document_not_triggered_when_not_a_signer(
    mock_delay, client, convention, logged_in_user
):
    convention.uuid = UUID("00000000-0000-0000-0000-000000000008")
    convention.statut = ConventionStatut.INSTRUCTION.label
    convention.save()

    response = client.post(
        reverse("conventions:regenerate_document", args=[convention.uuid])
    )

    assert response.status_code == 302
    mock_delay.assert_not_called()


@pytest.mark.django_db
def test_regenerate_document_rejects_get(client, convention, logged_in_user):
    response = client.get(
        reverse("conventions:regenerate_document", args=[convention.uuid])
    )

    assert response.status_code == 405
