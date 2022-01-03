from rest_framework import permissions
from conventions.models import Convention


class ConventionPermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        try:
            request.user.conventions().get(uuid=obj.uuid)
        except Convention.DoesNotExist:
            return False
        return True

    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user.has_perm("convention.view_convention")
        if request.method == "PUT":
            return request.user.has_perm("convention.change_convention")
        if request.method == "POST":
            return request.user.has_perm("convention.add_convention")
        if request.method == "DELETE":
            return request.user.has_perm("convention.delete_convention")
        return False
