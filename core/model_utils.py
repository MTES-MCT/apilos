import json


def get_field_key(instance, field_name, key):
    try:
        field = json.loads(getattr(instance, field_name))
        return field[key] if key in field else ""
    except json.decoder.JSONDecodeError:
        return ""
    except TypeError:
        return ""
