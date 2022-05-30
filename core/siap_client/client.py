import datetime
import uuid
import threading
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


class SingletonDoubleChecked:

    # resources shared by each and every
    # instance

    __singleton_lock = threading.Lock()
    __singleton_instance = None

    # define the classmethod
    @classmethod
    def get_instance(cls):

        # check for the singleton instance
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()

        # return the singleton instance
        return cls.__singleton_instance

    @classmethod
    def has_instance(cls):
        return bool(cls.__singleton_instance)


# Manage SiapClient as a Singleton
class SIAPClient(SingletonDoubleChecked):
    # pylint: disable=R0201

    siap_url = None

    def __init__(self) -> None:
        pass

    def get_siap_config(self) -> requests.Response:
        response = _call_siap_api("/config")
        return response.json()

    def get_habilitations(
        self, user_login: str, habilitation_id: int = 0
    ) -> requests.Response:
        response = _call_siap_api(
            "/habilitations",
            base_route="/services/habilitation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception("user doesn't have SAP habilitation")

    def get_menu(self, user_login: str, habilitation_id: int = 0) -> requests.Response:
        response = _call_siap_api(
            "/menu",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception("user doesn't have SAP habilitation")
