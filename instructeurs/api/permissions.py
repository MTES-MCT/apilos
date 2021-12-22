from rest_framework import permissions
from instructeurs.models import Administration


class AdministrationPermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        #        administration = Administration.objects.get(uuid=obj.uuid)
        #        return administration in request.user.administrations()
        try:
            request.user.administrations().get(uuid=obj.uuid)
        except Administration.DoesNotExist:
            return False
        return True

    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user.has_perm("administration.view_administration")
        if request.method == "PUT":
            return request.user.has_perm("administration.change_administration")
        if request.method == "POST":
            return request.user.has_perm("administration.add_administration")
        if request.method == "DELETE":
            return request.user.has_perm("administration.delete_administration")
        return False
