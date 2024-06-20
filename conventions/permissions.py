# Decorator that check the user has permission and scope to handle action
# for a given convention
from conventions.models.convention import Convention


def has_campaign_permission(permission):
    def has_permission(function):
        def wrapper(view, request, **kwargs):
            _check_campaign_permission(request, view.convention, permission)
            return function(view, request, **kwargs)

        return wrapper

    return has_permission


def has_campaign_permission_view_function(permission):
    def has_permission(function):
        def wrapper(request, convention_uuid, **kwargs):
            convention = Convention.objects.get(uuid=convention_uuid)
            _check_campaign_permission(request, convention, permission)
            return function(request, convention_uuid, **kwargs)

        return wrapper

    return has_permission


def _check_campaign_permission(request, convention, permission):
    role_id = (
        request.session["role"]["id"]
        if "role" in request.session and "id" in request.session["role"]
        else None
    )
    request.user.check_perm(permission, obj=convention, role_id=role_id)
