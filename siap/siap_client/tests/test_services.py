import pytest

from siap.siap_client.services import create_siap_alerte


def test_create_siap_alerte(settings, alerte):
    settings.USE_MOCKED_SIAP_CLIENT = True

    with pytest.raises(ValueError):
        create_siap_alerte(alerte)

    ret = create_siap_alerte(
        alerte=alerte, user_login="anakin@jedi.com", habilitation_id=1234
    )
    assert ret == {"message": "alerte créée avec succès"}
