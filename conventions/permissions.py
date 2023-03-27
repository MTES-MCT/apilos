# Decorator that check the user has permission and scope to handle action
# for a given convention
from conventions.models.convention import Convention


def has_campaign_permission(permission):
    def has_permission(function):
        def wrapper(view, request, **kwargs):
            request.user.check_perm(permission, view.convention)
            return function(view, request, **kwargs)

        return wrapper

    return has_permission


def has_campaign_permission_view_function(permission):
    def has_permission(function):
        def wrapper(request, convention_uuid, **kwargs):
            convention = Convention.objects.get(uuid=convention_uuid)
            request.user.check_perm(permission, convention)
            return function(request, convention_uuid, **kwargs)

        return wrapper

    return has_permission
