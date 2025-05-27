import logging
import threading
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

import jwt
import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from siap.exceptions import (
    FUSION_MESSAGE,
    NOT_FOUND_MESSAGE,
    TIMEOUT_MESSAGE,
    UNAUTHORIZED_MESSAGE,
    SIAPException,
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
    retry=retry_if_exception_type(SIAPException),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _call_siap_api(
    route: str,
    base_route: str = "",
    user_login: str = "",
    habilitation_id: int = 0,
    method: str = "GET",
    data: dict[str, Any] | None = None,
) -> requests.Response:
    siap_url = (
        settings.SIAP_CLIENT_HOST + base_route + settings.SIAP_CLIENT_PATH + route
    )

    jwt_token = build_jwt(user_login=user_login, habilitation_id=habilitation_id)

    headers = {
        "siap-Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }

    try:
        match method:
            case "GET":
                response = requests.get(siap_url, headers=headers, timeout=3)
            case "POST":
                response = requests.post(siap_url, data=data, headers=headers)
            case "DELETE":
                response = requests.delete(siap_url, headers=headers)
            case _:
                raise ValueError(f"Unsupported HTTP method: {method}")
    except (requests.ReadTimeout, requests.ConnectTimeout) as err:
        raise SIAPException(TIMEOUT_MESSAGE) from err

    if response.status_code == 401:
        error_text = UNAUTHORIZED_MESSAGE
        try:
            error_text += " : " + str(response.content["detail"])
        except KeyError:
            pass
        raise SIAPException(error_text)

    if response.status_code == 503:
        raise SIAPException(TIMEOUT_MESSAGE)

    if response.status_code >= 400:
        logger.error(
            "ERROR from SIAP API (route: %s, user_login: %s, habilitation_id: %s): %s",
            route,
            user_login,
            habilitation_id,
            response.content,
        )

    if settings.SIAP_CLIENT_LOG_API_CALLS:
        logger.warning(
            "[Status code: %s] SIAP API : %s, WITH JWT  : %s",
            response.status_code,
            response.content,
            jwt_token,
        )

    return response


def get_siap_credentials_from_request(request: HttpRequest) -> dict[str, Any]:
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


class SIAPClientInterface(ABC):
    def __init__(self) -> None:
        self.update_siap_config()

    @abstractmethod
    def update_siap_config(self) -> None: ...

    @abstractmethod
    def get_siap_config(self) -> dict: ...

    @abstractmethod
    def get_habilitations(self, user_login: str, habilitation_id: int = 0) -> dict: ...

    @abstractmethod
    def get_menu(self, user_login: str, habilitation_id: int) -> dict: ...

    @abstractmethod
    def get_operation(
        self, user_login: str, habilitation_id: int, operation_identifier: str
    ) -> dict: ...

    @abstractmethod
    def get_fusion(
        self, user_login: str, habilitation_id: int, bailleur_siren: str
    ) -> list: ...

    @abstractmethod
    def list_alertes(self, user_login: str, habilitation_id: int = 0) -> dict: ...

    @abstractmethod
    def create_alerte(
        self, user_login: str, habilitation_id: int, payload: dict[str, Any]
    ) -> dict: ...

    @abstractmethod
    def delete_alerte(self, user_login: str, habilitation_id: int) -> dict: ...


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


def validate_response(error_message: str = "SIAP error returned"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if response.status_code >= 200 and response.status_code < 300:
                if response.content:
                    return response.json()
                else:
                    return None
            raise SIAPException(f"{error_message}: {response.content}")

        return wrapper

    return decorator


# Manage SiapClient as a Singleton
class SIAPClientRemote(SIAPClientInterface):
    def get_siap_config(self) -> dict:
        response = _call_siap_api("/config")
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise PermissionDenied(f"SIAP error returned: {response.text}") from exc

    def update_siap_config(self) -> None:
        config = self.get_siap_config()
        if [
            k
            for k, v in config.items()
            if k in ["racineUrlAccesWeb", "urlAccesWeb", "urlAccesWebOperation"] and v
        ] != ["racineUrlAccesWeb", "urlAccesWeb", "urlAccesWebOperation"]:
            raise SIAPException(
                "La configuration SIAP-APILOS n'est pas bien formatée"
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

    @validate_response(error_message="user doesn't have SIAP habilitation")
    def get_menu(self, user_login: str, habilitation_id: int = 0) -> dict:
        return _call_siap_api(
            "/menu",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )

    @validate_response(
        error_message="user doesn't have enough rights to display operation"
    )
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
        raise SIAPException(UNAUTHORIZED_MESSAGE)

    @validate_response(error_message=FUSION_MESSAGE)
    def get_fusion(
        self, user_login: str, habilitation_id: int, bailleur_siren: str
    ) -> list:
        return _call_siap_api(
            f"/journalisation-fusion?siren={bailleur_siren}",
            base_route="/services/operation",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )

    @validate_response(error_message="user can't access alertes")
    def list_alertes(
        self, user_login: str, habilitation_id: int = 0
    ) -> list[dict[str, Any]]:
        return _call_siap_api(
            "/alertes",
            base_route="/services/tableaubord",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )

    @validate_response(error_message="user can't access alertes")
    def list_convention_alertes(
        self, convention_id: str, user_login: str, habilitation_id: int = 0
    ) -> list[dict[str, Any]]:
        return _call_siap_api(
            f"/alertes/convention/{convention_id}",
            base_route="/services/tableaubord",
            user_login=user_login,
            habilitation_id=habilitation_id,
        )

    @validate_response(error_message="user can't create alertes")
    def create_alerte(
        self, user_login: str, habilitation_id: int, payload: dict[str, Any]
    ) -> dict:
        return _call_siap_api(
            "/alertes",
            base_route="/services/tableaubord",
            user_login=user_login,
            habilitation_id=habilitation_id,
            method="POST",
            data=payload,
        )

    @validate_response(error_message="user can't update alertes")
    def delete_alerte(
        self, user_login: str, habilitation_id: int, alerte_id: str
    ) -> dict:
        return _call_siap_api(
            f"/alertes/{alerte_id}",
            base_route="/services/tableaubord",
            user_login=user_login,
            habilitation_id=habilitation_id,
            method="DELETE",
        )


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
        if (
            operation_identifier
            and operation_mock["donneesOperation"]["numeroOperation"]
            != operation_identifier
        ):
            raise SIAPException(NOT_FOUND_MESSAGE)
        return operation_mock

    def get_fusion(
        self, user_login: str, habilitation_id: int, bailleur_siren: str
    ) -> list:
        return fusion_mock

    def list_alertes(self, user_login, habilitation_id=0) -> list[dict[str, Any]]:
        return []

    def create_alerte(
        self, user_login: str, habilitation_id: int, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "message": "alerte créée avec succès",
        }

    def delete_alerte(self, user_login, habilitation_id) -> dict[str, Any]:
        return {
            "message": "alerte supprimée avec succès",
        }
