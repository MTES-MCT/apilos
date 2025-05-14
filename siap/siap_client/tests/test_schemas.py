from dataclasses import asdict
from datetime import date


def test_alerte_from_convention(alerte):
    assert asdict(alerte) == {
        "categorie_information": "CATEGORIE_ALERTE_ACTION",
        "code_commune": "64102",
        "code_gestion": "00020",
        "date_creation": date(2025, 1, 1),
        "destinataires": [{"role": "INSTRUCTEUR", "service": "MO"}],
        "etiquette": "CUSTOM",
        "etiquette_personnalisee": "Convention à instruire",
        "id_convention": "f1b9b923-225d-46a2-8527-df81d167cf06",
        "module": "APILOS",
        "nom_operation": "Programme 0",
        "num_convention": "123456789",
        "num_operation": "2239230177481",
        "siren": "453517732",
        "type_alerte": "Changement de statut",
        "url_direction": "/",
    }
