import logging
import datetime
import uuid
import threading
import requests
import jwt

from django.conf import settings

from siap.siap_client.mock_data import (
    config_mock,
    habilitations_mock,
    menu_mock,
    operation_mock,
)


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
    }
    if habilitation_id:
        payload["habilitation-id"] = habilitation_id

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
        timeout=5,
    )
    if response.status_code >= 400:
        logging.warning("error from SIAP API: %s", response.content)
    return response


class SIAPClient:

    __singleton_lock = threading.Lock()
    __singleton_instance = None

    # define the classmethod
    @classmethod
    def get_instance(cls):

        # check for the singleton instance
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    if settings.USE_MOCKED_SIAP_CLIENT:
                        print("SIAPClientMock")
                        cls.__singleton_instance = SIAPClientMock()
                    else:
                        print("SIAPClientRemote")
                        cls.__singleton_instance = SIAPClientRemote()

        # return the singleton instance
        return cls.__singleton_instance

    @classmethod
    def has_instance(cls):
        return bool(cls.__singleton_instance)


class SIAPClientInterface:
    def __init__(self) -> None:
        # pylint: disable=E1111
        config = self.get_siap_config()
        self.racine_url_acces_web = config["racineUrlAccesWeb"].rstrip("/")
        self.url_acces_web = config["urlAccesWeb"]
        self.url_acces_web_operation = config["urlAccesWebOperation"]

    def get_siap_config(self) -> dict:
        pass

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        pass

    def get_menu(self, user_login: str, habilitation_id: int) -> dict:
        pass

    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict:
        pass


def create_gestionnaire_if_not_exists(gestionnaire):
    return gestionnaire


def create_mo_if_not_exists(mo):
    return mo


def create_entity_from_habilitation_if_not_exists(habilitation):
    entity = None
    try:
        if habilitation["groupe"]["profil"]["code"] == "SER_GEST":
            create_gestionnaire_if_not_exists(habilitation["gestionnaire"])
        if habilitation["groupe"]["profil"]["code"] == "MO_PERS_MORALE":
            create_gestionnaire_if_not_exists(habilitation)
    except KeyError as e:
        raise KeyError("habilitation is not well formed") from e

    return entity


# Manage SiapClient as a Singleton
class SIAPClientRemote(SIAPClientInterface):
    def get_siap_config(self) -> dict:
        response = _call_siap_api("/config")
        return response.json()

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        response = _call_siap_api(
            "/habilitations",
            base_route="/services/habilitation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception(
            f"user doesn't have SIAP habilitation, SIAP error returned {response.content}"
        )

    def get_menu(self, user_login: str, habilitation_id: int = 0) -> dict:
        response = _call_siap_api(
            "/menu",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception(f"user doesn't have SIAP habilitation {response}")

    # /services/operation/api-int/v0/operation/{numeroOperation}
    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict:
        response = _call_siap_api(
            f"/operation/{operation_identifier}",
            base_route="/services/operation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise Exception(
            f"user doesn't have enough rights to display operation {response}"
        )


# Manage SiapClient as a Singleton
class SIAPClientMock(SIAPClientInterface):
    def get_siap_config(self) -> dict:
        return config_mock

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        return habilitations_mock

    def get_menu(self, user_login: str, habilitation_id: int = 0) -> dict:
        return menu_mock

    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict:
        return operation_mock
