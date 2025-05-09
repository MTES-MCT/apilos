from typing import Any

from django.http import HttpRequest

from .client import SIAPClient
from .schemas import Alerte


def siap_credentials_from_request(request: HttpRequest) -> dict[str, Any]:
    """
    Get the user login and habilitation ID from the request.
    """
    user_login = request.user.cerbere_login
    habilitation_id = request.session.get("habilitation_id")

    if not user_login or not habilitation_id:
        raise ValueError("user_login and habilitation_id are required")

    return {
        "user_login": user_login,
        "habilitation_id": habilitation_id,
    }


def create_siap_alerte(alerte: Alerte, request: HttpRequest) -> dict[str, Any]:
    return SIAPClient.get_instance().create_alerte(
        payload=alerte.to_json(),
        **siap_credentials_from_request(request),
    )


def delete_siap_alerte(alerte_id: str, request: HttpRequest) -> dict[str, Any]:
    return SIAPClient.get_instance().delete_alerte(
        alerte_id=alerte_id,
        **siap_credentials_from_request(request),
    )
