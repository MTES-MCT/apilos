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
    return jwt.encode(
        payload,
        settings.SIAP_CLIENT_JWT_SIGN_KEY,
        algorithm=settings.SIAP_CLIENT_ALGORITHM,
    )


# Manage singleton ?
class SIAPClient:
    siap_url = None

    def __init__(self) -> None:
        self.siap_url = settings.SIAP_CLIENT_HOST + settings.SIAP_CLIENT_PATH

    def _call_siap_api(self, route: str, user_login: str = "") -> requests.Response:
        siap_url_config = self.siap_url + route
        response = requests.get(
            siap_url_config,
            headers={
                "siap-Authorization": f"Bearer {_build_jwt(user_login=user_login)}"
            },
        )
        return response

    def get_config(self) -> requests.Response:
        return self._call_siap_api("/config")

    def get_habilitations(self, user_login: str) -> requests.Response:
        return self._call_siap_api("/habilitations", user_login)
