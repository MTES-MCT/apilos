import pytest
import time_machine

from core.tests.factories import ConventionFactory
from siap.siap_client.schemas import Alerte, Destinataire


@pytest.fixture
@time_machine.travel("2025-01-01")
def alerte() -> Alerte:
    convention = ConventionFactory.build(
        uuid="f1b9b923-225d-46a2-8527-df81d167cf06",
        numero="123456789",
        programme__administration__code="00020",
        programme__bailleur__siren="453517732",
        programme__code_insee_commune="64102",
        programme__nom="Programme 0",
        programme__numero_operation="2239230177481",
    )

    return Alerte.from_convention(
        convention=convention,
        categorie_information="CATEGORIE_ALERTE_ACTION",
        destinataires=[
            Destinataire(role="INSTRUCTEUR", service="MO"),
        ],
        etiquette="CUSTOM",
        etiquette_personnalisee="Convention à instruire",
        type_alerte="Changement de statut",
        url_direction="/",
    )
