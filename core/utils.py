import json
import uuid
from typing import Any, SupportsRound


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


def get_uuid_or_none(uuid_or_string):
    return is_valid_uuid(uuid_or_string)


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
