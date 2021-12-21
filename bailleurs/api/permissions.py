from rest_framework import permissions
from bailleurs.models import Bailleur


class BailleurPermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        try:
            request.user.bailleurs().get(uuid=obj.uuid)
        except Bailleur.DoesNotExist:
            return False
        return True

    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user.has_perm("bailleur.view_bailleur")
        if request.method == "PUT":
            return request.user.has_perm("bailleur.change_bailleur")
        if request.method == "POST":
            return request.user.has_perm("bailleur.add_bailleur")
        if request.method == "DELETE":
            return request.user.has_perm("bailleur.delete_bailleur")
        return False
