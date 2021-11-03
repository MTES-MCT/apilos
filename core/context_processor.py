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
def has_own_comment(comments, user_id):
    print(user_id)
    print(comments)
    print(map(lambda x: x.user_id, comments))

    return user_id in map(lambda x: x.user_id, comments)
