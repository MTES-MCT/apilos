from typing import Any

from .siap_client.client import SIAPClient
from .siap_client.schemas import Alerte


def create_siap_alerte(
    alerte: Alerte, user_login: str, habilitation_id: int
) -> dict[str, Any]:
    return SIAPClient.get_instance().create_alerte(
        user_login=user_login,
        habilitation_id=habilitation_id,
        payload=alerte.to_json(),
    )
