from django.template.defaulttags import register
from core import settings


def get_environment(request):
    data = {}
    data["ENVIRONMENT"] = settings.ENVIRONMENT
    return data


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def item_exists(dictionary, key):
    return dictionary.get(key, "FALSE_PLACEHOLDER") == "FALSE_PLACEHOLDER"
