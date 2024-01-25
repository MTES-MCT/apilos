# Decorator that check the user has permission and scope to handle action
# for a given convention


def has_campaign_permission(permission):
    def has_permission(function):
        def wrapper(view, request, **kwargs):
            request.user.check_perm(permission, view.convention)
            return function(view, request, **kwargs)

        return wrapper

    return has_permission
