import logging
import threading
import uuid
from datetime import datetime, timedelta

import jwt
import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from siap.exceptions import (
    SIAPException,
    TimeoutSIAPException,
    UnauthorizedSIAPException,
    UnavailableServiceSIAPException,
)
from siap.siap_client.mock_data import (
    config_mock,
    fusion_mock,
    habilitations_mock,
    menu_mock,
    operation_mock,
)

# The SIAP configuration will be refresh every REFRESH_SIAP_CONFIG minutes
REFRESH_SIAP_CONFIG = 60

logger = logging.getLogger(__name__)


def build_jwt(user_login: str = "", habilitation_id: int = 0) -> str:
    dt_iat = datetime.now()
    dt_exp = dt_iat + timedelta(minutes=5)
    ts_iat = int(dt_iat.timestamp())
    ts_exp = int(dt_exp.timestamp())
    payload = {
        "token_type": "access",
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


@retry(
    retry=retry_if_exception_type(TimeoutSIAPException),
    stop=stop_after_attempt(3),
    reraise=True,
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
    myjwt = build_jwt(user_login=user_login, habilitation_id=habilitation_id)
    try:
        response = requests.get(
            siap_url_config,
            headers={"siap-Authorization": f"Bearer {myjwt}"},
            timeout=3,
        )
    except (requests.ReadTimeout, requests.ConnectTimeout) as e:
        raise TimeoutSIAPException() from e
    if response.status_code == 401:
        error_text = "Unauthorized"
        try:
            error_text = str(response.content["detail"])
        except Exception:
            pass
        raise UnauthorizedSIAPException(error_text)
    if response.status_code == 503:
        raise UnavailableServiceSIAPException()
    if response.status_code >= 400:
        logger.error("ERROR from SIAP API: %s", response.content)
    logger.warning(
        "[Status code: %s] SIAP API : %s, WITH JWT  : %s",
        response.status_code,
        response.content,
        myjwt,
    )
    return response


class SIAPClient:
    __singleton_lock = threading.Lock()
    __singleton_instance = None
    __should_update_at = datetime.now() + timedelta(minutes=REFRESH_SIAP_CONFIG)

    # define the classmethod
    @classmethod
    def get_instance(cls):
        # check for the singleton instance
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    if settings.USE_MOCKED_SIAP_CLIENT:
                        cls.__singleton_instance = SIAPClientMock()
                    else:
                        cls.__singleton_instance = SIAPClientRemote()
        if cls.__should_update_at < datetime.now():
            cls.__singleton_instance.update_siap_config()
            cls.__should_update_at = datetime.now() + timedelta(
                minutes=REFRESH_SIAP_CONFIG
            )

        # return the singleton instance
        return cls.__singleton_instance

    @classmethod
    def has_instance(cls):
        return bool(cls.__singleton_instance)


class SIAPClientInterface:
    def __init__(self) -> None:
        self.update_siap_config()

    def update_siap_config(self) -> None:
        pass

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
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            raise PermissionDenied(f"SIAP error returned: {response.text}")

    def update_siap_config(self) -> None:
        config = self.get_siap_config()
        if [
            k
            for k, v in config.items()
            if k in ["racineUrlAccesWeb", "urlAccesWeb", "urlAccesWebOperation"] and v
        ] != ["racineUrlAccesWeb", "urlAccesWeb", "urlAccesWebOperation"]:
            raise SIAPException(
                "SIAP configuration is not well formed"
                ", racineUrlAccesWeb: {}"
                ", urlAccesWeb: {}"
                ", urlAccesWebOperation: {}".format(
                    config["racineUrlAccesWeb"],
                    config["urlAccesWeb"],
                    config["urlAccesWebOperation"],
                )
            )
        self.racine_url_acces_web = config["racineUrlAccesWeb"].rstrip("/")
        self.url_acces_web = config["urlAccesWeb"]
        self.url_acces_web_operation = config["urlAccesWebOperation"]

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        response = _call_siap_api(
            "/habilitations",
            base_route="/services/habilitation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                if habilitation_id:
                    return self.get_habilitations(user_login, 0)
        raise PermissionDenied(
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
        raise SIAPException(
            f"user doesn't have enough rights to display operation {response}"
        )

    def get_fusion(
        self, user_login: str, habilitation_id: int, bailleur_siren: str
    ) -> list:
        # /services/operation/api-int/v0/journalisation-fusion?siren=
        response = _call_siap_api(
            f"/journalisation-fusion?siren={bailleur_siren}",
            base_route="/services/operation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise SIAPException(f"SIAP error returned {response.content}")


# Manage SiapClient as a Singleton
class SIAPClientMock(SIAPClientInterface):
    def get_siap_config(self) -> dict:
        return config_mock

    def update_siap_config(self) -> None:
        config = self.get_siap_config()
        self.racine_url_acces_web = config["racineUrlAccesWeb"].rstrip("/")
        self.url_acces_web = config["urlAccesWeb"]
        self.url_acces_web_operation = config["urlAccesWebOperation"]

    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict:
        return habilitations_mock

    def get_menu(self, user_login: str, habilitation_id: int = 0) -> dict:
        return menu_mock

    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict:
        return operation_mock

    def get_fusion(
        self, user_login: str, habilitation_id: int, bailleur_siren: str
    ) -> list:
        return fusion_mock
