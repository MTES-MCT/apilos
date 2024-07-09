from unittest.mock import Mock, patch

import pytest
from django.test import RequestFactory

from bailleurs.tests.factories import BailleurFactory
from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from conventions.tests.factories import ConventionFactory
from conventions.views import save_convention
from conventions.views.conventions import validate_convention
from instructeurs.tests.factories import AdministrationFactory
from programmes.tests.factories import ProgrammeFactory
from users.tests.factories import GroupFactory, RoleFactory, UserFactory
from users.type_models import TypeRole


@pytest.mark.django_db
def test_get_contributors():
    # Create a new convention en projet
    bailleur = BailleurFactory()
    administration = AdministrationFactory()
    programme = ProgrammeFactory(bailleur=bailleur, administration=administration)
    convention = ConventionFactory(
        statut=ConventionStatut.PROJET.label, lot__programme=programme
    )

    # Create a user bailleur and a user instructeur
    user_bailleur = UserFactory()
    RoleFactory(
        user=user_bailleur,
        bailleur=bailleur,
        typologie=TypeRole.BAILLEUR,
        group=GroupFactory(name="Bailleur", rw=["logement", "convention"]),
    )
    user_instructeur = UserFactory()
    RoleFactory(
        user=user_instructeur,
        administration=administration,
        typologie=TypeRole.INSTRUCTEUR,
        group=GroupFactory(name="Instructeur", rwd=["logement", "convention"]),
    )

    # Submit the convention to instruction with a bailleur
    request = RequestFactory().post("/", {"SubmitConvention": True})
    request.session = "session"
    request.user = user_bailleur
    save_convention(request, convention.uuid)

    # Bailleur should appear in contributors
    assert convention.get_contributors() == {
        "instructeurs": [],
        "bailleurs": [(user_bailleur.first_name, user_bailleur.last_name)],
    }

    # Validate convention with an instructeur
    request = RequestFactory().post("/", {"convention_numero": "1234"})
    request.session = "session"
    request.user = user_instructeur
    with patch("conventions.tasks.task_generate_and_send.delay", Mock()):
        validate_convention(request, convention.uuid)

    # The instructor should appear in contributors
    assert convention.get_contributors() == {
        "instructeurs": [(user_instructeur.first_name, user_instructeur.last_name)],
        "bailleurs": [(user_bailleur.first_name, user_bailleur.last_name)],
    }


@pytest.mark.django_db
@patch.object(Convention, "get_contributors")
def test_format_contributors_empty(mock_get_contributors):
    mock_get_contributors.return_value = {"instructeurs": [], "bailleurs": []}
    convention = ConventionFactory()
    assert convention.format_contributors() == "aucun contributeur connu pour l'instant"


@pytest.mark.django_db
@patch.object(Convention, "get_contributors")
def test_format_contributors(mock_get_contributors):
    mock_get_contributors.return_value = {
        "instructeurs": [("John", "Doe"), ("Alice", "Tokyo"), ("Jean", "Madrid")],
        "bailleurs": [("Sarah", "Berlin")],
    }
    convention = ConventionFactory()
    assert (
        convention.format_contributors()
        == "pour l'instruction John Doe, Alice Tokyo, Jean Madrid et pour le bailleur Sarah Berlin"
    )
