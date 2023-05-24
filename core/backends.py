"""
Manage Auth backends
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpRequest
from django_cas_ng.backends import CASBackend

from users.models import GroupProfile


class CerbereCASBackend(CASBackend):
    """
    Auth backend for CERBERE
    """

    def user_can_authenticate(self, user):
        return True


class MockedCerbereCASBackend(CerbereCASBackend):
    """
    Backend d'authentifcation truqué pour remplacer CERBERE. À n'utiliser qu'en
    développement ou pour les tests unitaires.

    Résoud le ticker utilisateur par l'identifiant Cerbère.
    """

    def authenticate(self, request: HttpRequest, ticket: str, service: str):
        return get_user_model().objects.filter(cerbere_login=ticket).first()


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
                if user.is_staff or user.is_superuser:
                    request.session["currently"] = GroupProfile.STAFF
                    request.session["is_staff"] = True
                elif user.is_bailleur():
                    request.session["currently"] = GroupProfile.BAILLEUR
                elif user.is_instructeur():
                    request.session["currently"] = GroupProfile.INSTRUCTEUR
                    admin_ids = user.administration_ids()
                    request.session["multi_administration"] = (
                        admin_ids == [] or len(admin_ids) > 1
                    )
            return user
        return None
