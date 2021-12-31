from rest_framework import permissions
from programmes.models import Programme, Lot


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


class LotPermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        try:
            lot = Lot.objects.get(uuid=obj.uuid)
            request.user.programmes().get(id=lot.programme_id)
        except Lot.DoesNotExist:
            return False
        except Programme.DoesNotExist:
            return False
        return True

    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user.has_perm("lot.view_lot")
        if request.method == "PUT":
            return request.user.has_perm("lot.change_lot")
        if request.method == "POST":
            return request.user.has_perm("lot.add_lot")
        if request.method == "DELETE":
            return request.user.has_perm("lot.delete_lot")
        return False
