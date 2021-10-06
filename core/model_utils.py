import json


def get_field_key(instance, field_name, key, default=""):
    try:
        field = json.loads(getattr(instance, field_name))
        return field[key] if key in field else ""
    except json.decoder.JSONDecodeError:
        return default
    except TypeError:
        return default
