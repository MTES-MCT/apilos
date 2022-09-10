import json


def get_field_key(instance, field_name, key, default=""):
    try:
        field = json.loads(getattr(instance, field_name))
        return field[key] if key in field else ""
    except json.decoder.JSONDecodeError:
        return default
    except TypeError:
        return default


def get_key_from_json_field(json_field, key, default=""):
    try:
        field = json.loads(json_field)
        return field[key] if key in field else ""
    except json.decoder.JSONDecodeError:
        return default
    except TypeError:
        return default
