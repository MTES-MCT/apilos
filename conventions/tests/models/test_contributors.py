from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command
from django.test import RequestFactory

from bailleurs.tests.factories import BailleurFactory
from conventions.models.choices import ConventionStatut
from conventions.views import save_convention
from conventions.views.conventions import validate_convention
from core.tests.factories import ConventionFactory, ProgrammeFactory
from instructeurs.tests.factories import AdministrationFactory
from users.tests.factories import GroupFactory, RoleFactory, UserFactory
from users.type_models import TypeRole


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "auth.json")


@pytest.mark.django_db
def test_get_contributors():
    # Create a new convention en projet
    bailleur = BailleurFactory()
    administration = AdministrationFactory()
    programme = ProgrammeFactory(bailleur=bailleur, administration=administration)
    convention = ConventionFactory(
        statut=ConventionStatut.PROJET.label,
        programme=programme,
        create_lot=True,
    )

    # Create a user bailleur and a user instructeur
    user_bailleur = UserFactory()
    RoleFactory(
        user=user_bailleur,
        bailleur=bailleur,
        typologie=TypeRole.BAILLEUR,
        group=GroupFactory(name="bailleur"),
    )
    user_instructeur = UserFactory()
    RoleFactory(
        user=user_instructeur,
        administration=administration,
        typologie=TypeRole.INSTRUCTEUR,
        group=GroupFactory(name="instructeur"),
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
        "number": 1,
    }

    # Validate convention with an instructeur
    request = RequestFactory().post(
        "/", {"convention_numero": "1234", "finalisationform": True}
    )
    request.session = "session"
    request.user = user_instructeur
    with patch("conventions.tasks.task_generate_and_send.delay", Mock()):
        validate_convention(request, convention.uuid)

    # The instructor should appear in contributors
    assert convention.get_contributors() == {
        "instructeurs": [(user_instructeur.first_name, user_instructeur.last_name)],
        "bailleurs": [(user_bailleur.first_name, user_bailleur.last_name)],
        "number": 2,
    }
