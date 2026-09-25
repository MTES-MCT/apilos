import json
import logging
import unicodedata
import uuid
from typing import Any, SupportsRound

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)


def round_half_up(number: SupportsRound[Any], ndigits: int = 0):
    """
    python 3 round number following "round half to even" way
    It doesn't fit the UE norm which is a "round half up" way
    round_half_up follow the UE norm way of round
    """
    if ndigits == 0:
        return round(float(number) + 1e-15)
    return round(float(number) + 1e-15, ndigits)


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def get_key_from_json_field(json_field, key, default=""):
    try:
        field = json.loads(json_field)
        return field[key] if key in field else ""
    except json.decoder.JSONDecodeError:
        return default
    except TypeError:
        return default


def custom_history_user_setter(instance, history_user):
    """
    Used by django_simple_history to set the history_user_id because sometimes the user is
    not saved in DB, when the API is called from SIAP for example.
    So we can't use the user.pk, we use set it to None.
    """
    instance.history_user_id = (
        history_user.pk if history_user and history_user.pk else None
    )


def make_random_string(length: int = 10) -> str:
    return get_random_string(
        length,
        allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789",
    )


def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def check_user_whitelist(user):
    if settings.ENABLE_LOGIN_WHITELIST:
        allowed_logins_str = settings.ALLOWED_LOGINS
        allowed_logins = [
            login.strip() for login in allowed_logins_str.split(",") if login.strip()
        ]
        if user.cerbere_login not in allowed_logins:
            logger.error(
                f"Accès rejeté par la liste blanche pour le login: {user.cerbere_login}"
            )
            raise PermissionDenied(
                "Votre compte n'est pas autorisé à accéder à cette application."
            )
