from typing import Any

from django.http import HttpRequest

from .client import SIAPClient
from .schemas import Alerte


def create_siap_alerte(
    alerte: Alerte,
    request: HttpRequest | None = None,
    user_login: str | None = None,
    habilitation_id: int | None = None,
) -> dict[str, Any]:

    _user_login = None
    _habilitation_id = None

    if request:
        _user_login = request.user.cerbere_login
        _habilitation_id = request.session.get("habilitation_id")
    if user_login:
        _user_login = user_login
    if habilitation_id:
        _habilitation_id = habilitation_id

    if not _user_login or not _habilitation_id:
        raise ValueError("user_login and habilitation_id are required")

    return SIAPClient.get_instance().create_alerte(
        user_login=_user_login,
        habilitation_id=_habilitation_id,
        payload=alerte.to_json(),
    )
