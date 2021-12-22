from rest_framework import permissions
from programmes.models import Programme


class ProgrammePermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        try:
            request.user.programmes().get(uuid=obj.uuid)
        except Programme.DoesNotExist:
            return False
        return True

    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user.has_perm("programme.view_programme")
        if request.method == "PUT":
            return request.user.has_perm("programme.change_programme")
        if request.method == "POST":
            return request.user.has_perm("programme.add_programme")
        if request.method == "DELETE":
            return request.user.has_perm("programme.delete_programme")
        return False
