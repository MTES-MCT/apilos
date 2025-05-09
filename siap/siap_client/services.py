from typing import Any

from django.http import HttpRequest

from .client import SIAPClient
from .schemas import Alerte


def get_siap_credentials(request: HttpRequest) -> tuple[str, int]:
    """
    Get the user login and habilitation ID from the request.
    """
    user_login = request.user.cerbere_login
    habilitation_id = request.session.get("habilitation_id")

    if not user_login or not habilitation_id:
        raise ValueError("user_login and habilitation_id are required")

    return user_login, habilitation_id


def create_siap_alerte(alerte: Alerte, request: HttpRequest) -> dict[str, Any]:
    user_login, habilitation_id = get_siap_credentials(request)
    return SIAPClient.get_instance().create_alerte(
        user_login=user_login,
        habilitation_id=habilitation_id,
        payload=alerte.to_json(),
    )


def delete_siap_alerte(alerte_id: str, request: HttpRequest) -> dict[str, Any]:
    user_login, habilitation_id = get_siap_credentials(request)
    return SIAPClient.get_instance().delete_alerte(
        user_login=user_login,
        habilitation_id=habilitation_id,
        alerte_id=alerte_id,
    )
