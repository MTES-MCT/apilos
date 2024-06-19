# Decorator that check the user has permission and scope to handle action
# for a given convention
from conventions.models.convention import Convention


def has_campaign_permission(permission):
    def has_permission(function):
        def wrapper(view, request, **kwargs):
            role_id = (
                request.session["role"]["id"]
                if "id" in request.session["role"]
                else None
            )
            request.user.check_perm(permission, obj=view.convention, role_id=role_id)
            return function(view, request, **kwargs)

        return wrapper

    return has_permission


def has_campaign_permission_view_function(permission):
    def has_permission(function):
        def wrapper(request, convention_uuid, **kwargs):
            convention = Convention.objects.get(uuid=convention_uuid)
            role_id = (
                request.session["role"]["id"]
                if "id" in request.session["role"]
                else None
            )
            request.user.check_perm(permission, obj=convention, role_id=role_id)
            return function(request, convention_uuid, **kwargs)

        return wrapper

    return has_permission
