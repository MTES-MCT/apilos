import datetime
import uuid
import requests
import jwt

from django.conf import settings


def _build_jwt(user_login: str = "", habilitation_id: int = 0) -> str:
    dt_iat = datetime.datetime.now()
    dt_exp = dt_iat + datetime.timedelta(minutes=5)
    ts_iat = int(dt_iat.timestamp())
    ts_exp = int(dt_exp.timestamp())
    payload = {
        "iat": ts_iat,
        "exp": ts_exp,
        "jti": str(uuid.uuid4()),
        "user-login": user_login,
        "habilitation-id": habilitation_id,
    }
    print(payload)
    return jwt.encode(
        payload,
        settings.SIAP_CLIENT_JWT_SIGN_KEY,
        algorithm=settings.SIAP_CLIENT_ALGORITHM,
    )


def _call_siap_api(
    route: str,
    base_route: str = "",
    user_login: str = "",
    habilitation_id: int = 0,
) -> requests.Response:
    siap_url_config = (
        settings.SIAP_CLIENT_HOST + base_route + settings.SIAP_CLIENT_PATH + route
    )
    myjwt = _build_jwt(user_login=user_login, habilitation_id=habilitation_id)
    response = requests.get(
        siap_url_config,
        headers={"siap-Authorization": f"Bearer {myjwt}"},
    )
    return response


# Manage singleton ?
class SIAPClient:
    # pylint: disable=R0201

    siap_url = None

    def __init__(self) -> None:
        pass

    def get_config(self) -> requests.Response:
        return _call_siap_api("/config")

    def get_habilitations(
        self, user_login: str, habilitation_id: int = 0
    ) -> requests.Response:
        return _call_siap_api(
            "/habilitations",
            base_route="/services/habilitation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
