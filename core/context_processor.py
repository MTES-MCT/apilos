from django.template.defaulttags import register
from core import settings


def get_environment(request):
    data = {}
    data["ENVIRONMENT"] = settings.ENVIRONMENT
    return data


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")


@register.filter
def item_exists(dictionary, key):
    return dictionary.get(key, "FALSE_PLACEHOLDER") == "FALSE_PLACEHOLDER"


@register.filter
def has_own_active_comment(comments, user_id):
    return user_id in list(
        map(
            lambda x: x.user_id,
            filter(lambda comment: comment.statut != "CLOS", comments),
        )
    )


@register.filter
def add_uuid(label, uuid_to_add):
    return f"{label}{uuid_to_add}"
