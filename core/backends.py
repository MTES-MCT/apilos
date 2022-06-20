"""
Manage Auth backends
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from django_cas_ng.backends import CASBackend


class CerbereCASBackend(CASBackend):
    """
    Auth backend for CERBERE
    """

    def user_can_authenticate(self, user):
        return True


UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """
    Default Django auth backend
    Accept email and username
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            user = (
                UserModel.objects.filter(
                    Q(username__iexact=username) | Q(email__iexact=username)
                )
                .order_by("id")
                .first()
            )

        if user.check_password(password) and self.user_can_authenticate(user):
            if request is not None:
                request.session["is_staff"] = user.is_staff
                request.session["is_instructeur"] = user.is_instructeur()
                request.session["is_bailleur"] = user.is_bailleur()
            return user
        return None
