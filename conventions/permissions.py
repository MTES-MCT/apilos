from conventions.models import Convention

# Decorator that check the user has permission and scope to handle action
# for a given convention
def has_campaign_permission(permission):
    def has_permission(function):
        def wrapper(view, request, **kwargs):
            convention_uuid = kwargs.get("convention_uuid", None)
            if convention_uuid:
                convention = Convention.objects.get(uuid=convention_uuid)
                request.user.check_perm(permission, convention)
            else:
                request.user.check_perm(permission)
            return function(view, request, **kwargs)

        return wrapper

    return has_permission
