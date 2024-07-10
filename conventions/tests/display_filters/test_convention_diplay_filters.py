from unittest.mock import patch

import pytest

from conventions.models.convention import Convention
from conventions.templatetags.display_filters import display_contributors
from conventions.tests.factories import ConventionFactory


@pytest.mark.django_db
@patch.object(Convention, "get_contributors")
def test_format_contributors_empty(mock_get_contributors):
    mock_get_contributors.return_value = {"instructeurs": [], "bailleurs": []}
    convention = ConventionFactory()
    assert display_contributors(convention) == "aucun contributeur connu pour l'instant"


@pytest.mark.django_db
@patch.object(Convention, "get_contributors")
def test_format_contributors(mock_get_contributors):
    mock_get_contributors.return_value = {
        "instructeurs": [("John", "Doe"), ("Alice", "Tokyo"), ("Jean", "Madrid")],
        "bailleurs": [("Sarah", "Berlin")],
    }
    convention = ConventionFactory()
    assert (
        display_contributors(convention)
        == "pour l'instruction John Doe, Alice Tokyo, Jean Madrid et pour le bailleur Sarah Berlin"
    )
