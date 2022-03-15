from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.db import models

from bailleurs.models import Bailleur
from conventions.models import Convention, ConventionStatut
from instructeurs.models import Administration
from programmes.models import Lot, Programme

from users.type_models import TypeRole


class slist(list):
    @property
    def length(self):
        return len(self)


class EmailPreferences(models.TextChoices):
    # Toutes les conventions : L'utilisateur reçoit tous les emails pour toutes les conventions
    # dans son périmètre (selon ses filtres géographiques s'ils sont configurés)
    TOUS = "TOUS", "Tous les emails"
    # L'utilisateur reçoit tous les emails des conventions qu'il instruit
    # L'utilisateur instructeur reçoit les emails des conventions nouvellement à instruire
    PARTIEL = "PARTIEL", "Emails des conventions instruites"
    # L'utilisateur ne reçoit pas les emails relatifs aux conventions
    AUCUN = "AUCUN", "Aucun email"


class User(AbstractUser):
    # pylint: disable=R0904

    administrateur_de_compte = models.BooleanField(default=False)
    telephone = models.CharField(
        null=True,
        max_length=25,
    )
    preferences_email = models.CharField(
        max_length=25,
        choices=EmailPreferences.choices,
        default=EmailPreferences.TOUS,
    )

    def has_object_permission(self, obj):
        if isinstance(obj, Convention):
            # is bailleur of the convention or is instructeur of the convention
            return self.role_set.filter(
                bailleur_id=obj.bailleur_id
            ) or self.role_set.filter(administration_id=obj.programme.administration_id)
        if isinstance(obj, Lot):
            # is bailleur of the convention or is instructeur of the convention
            return self.role_set.filter(
                bailleur_id=obj.bailleur_id
            ) or self.role_set.filter(administration_id=obj.programme.administration_id)
        raise Exception(
            "Les permissions ne sont pas correctement configurer, un "
            + "objet de type Convention doit être asocié à la "
            + "permission 'change_convention'"
        )

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        # check object permission
        if obj is not None:
            if not self.has_object_permission(obj):
                return False
            # forbid to change close convention
            if perm == "convention.change_convention" and isinstance(obj, Convention):
                if obj.statut == ConventionStatut.CLOS:
                    return False
        # check permission itself
        permissions = []
        for role in self.role_set.all():
            permissions += map(
                lambda permission: permission.content_type.name
                + "."
                + permission.codename,
                role.group.permissions.all(),
            )
        return perm in permissions

    def check_perm(self, perm, obj=None):
        if not self.has_perm(perm, obj):
            raise PermissionDenied

    def is_bailleur(self, bailleur_id=None):
        if bailleur_id is not None:
            return self.roles.filter(bailleur_id=bailleur_id)
        return self._is_role(TypeRole.BAILLEUR) or self.is_superuser

    def is_instructeur(self):
        return self._is_role(TypeRole.INSTRUCTEUR) or self.is_superuser

    def _is_role(self, role):
        return role in map(lambda r: r.typologie, self.role_set.all())

    #
    # list of programme following role
    # super admin = all programme, filtre = {}
    # instructeur = all programme following geo, filtre = {}
    # bailleur = programme which belongs to the bailleurs, filtre = {bailleur_id__in: [x,y,z]}
    # else raise
    #
    def programme_filter(self, prefix=""):
        if self.is_superuser:
            return {}

        # to do : manage programme related to geo for instructeur
        if self.is_instructeur():
            return {prefix + "administration_id__in": self._administration_ids()}

        if self.is_bailleur():
            return {prefix + "bailleur_id__in": self._bailleur_ids()}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permettant le filtre sur les programmes"
        )

    def programmes(self):
        return Programme.objects.filter(**self.programme_filter())

    #
    # list of administration following role
    # super admin = all administration, filtre = {}
    # instructeur = ???, filtre = {}
    # bailleur = ???, filtre = {}
    # else raise
    #
    def administration_filter(self):
        if self.is_superuser:
            return {}

        # to do : manage programme related to geo for instructeur
        if self.is_instructeur():
            return {"id__in": self._administration_ids()}

        # to do : manage programme related to geo for bailleur
        if self.is_bailleur():
            return {"id__in": []}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permettant le "
            + "filtre sur les administrations"
        )

    def _administration_ids(self):
        return list(
            map(
                lambda role: role.administration_id,
                self.role_set.filter(typologie=TypeRole.INSTRUCTEUR),
            )
        )

    def administrations(self, order_by="nom"):
        return Administration.objects.filter(**self.administration_filter()).order_by(
            order_by
        )

    #
    # list of bailleurs following role
    # super admin = all bailleurs, filtre = {}
    # instructeur = all bailleurs following geo, filtre = {}
    # bailleur = bailleurs which belongs to the user as a bailleur, filtre = {id__in: [x,y,z]}
    # else raise
    #
    def bailleur_filter(self):
        if self.is_superuser:
            return {}

        # to do : manage programme related to geo for instructeur
        if self.is_instructeur():
            return {"id__in": []}

        if self.is_bailleur():
            return {"id__in": self._bailleur_ids()}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permettant le filtre sur les bailleurs"
        )

    def _bailleur_ids(self):
        return list(
            map(
                lambda role: role.bailleur_id,
                self.role_set.filter(typologie=TypeRole.BAILLEUR),
            )
        )

    def bailleurs(self, order_by="nom"):
        return Bailleur.objects.filter(**self.bailleur_filter()).order_by(order_by)

    def convention_filter(self):
        if self.is_superuser:
            return {}

        # to do : manage programme related to geo for instructeur
        if self.is_instructeur():
            return {"programme__administration_id__in": self._administration_ids()}

        if self.is_bailleur():
            return {"bailleur_id__in": self._bailleur_ids()}

        raise PermissionDenied(
            "L'utilisateur courant n'a pas de role associé permettant le filtre sur les bailleurs"
        )

    def conventions(self):
        return Convention.objects.filter(**self.convention_filter())

    def full_editable_convention(self, convention):
        # is bailleur of the convention
        if self.role_set.filter(bailleur_id=convention.bailleur_id):
            return convention.statut == ConventionStatut.BROUILLON
        # is instructeur of the convention
        if self.role_set.filter(
            administration_id=convention.programme.administration_id
        ):
            return convention.statut in [
                ConventionStatut.INSTRUCTION,
                ConventionStatut.CORRECTION,
            ]
        return False

    def user_list(self, order_by="username"):
        if self.is_superuser:
            return User.objects.all().order_by(order_by)
        if self.is_bailleur():
            return (
                User.objects.all()
                .filter(role__bailleur_id__in=self._bailleur_ids())
                .order_by(order_by)
                .distinct()
            )
        if self.is_instructeur():
            return (
                User.objects.all()
                .filter(role__administration_id__in=self._administration_ids())
                .order_by(order_by)
                .distinct()
            )
        raise Exception(
            "L'utilisateur courant n'a pas de role associé permettant de"
            + " filtrer les utilisateurs"
        )

    def is_administrator(self, user=None):
        if self.is_superuser:
            return True
        if not self.administrateur_de_compte:
            return False
        if user is None:
            return True
        if user.is_superuser:
            return False
        # check if the scope of current_user and user is not empty
        if list(set(user.bailleurs()) & set(self.bailleurs())) or list(
            set(user.administrations()) & set(self.administrations())
        ):
            return True
        return False

    def is_administration_administrator(self, administration):
        if self.is_superuser:
            return True
        if not self.administrateur_de_compte:
            return False
        if administration in self.administrations():
            return True
        return False

    def is_bailleur_administrator(self, bailleur):
        if self.is_superuser:
            return True
        if not self.administrateur_de_compte:
            return False
        if bailleur in self.bailleurs():
            return True
        return False

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name}".strip()
            if self.first_name or self.last_name
            else self.username
        )


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    typologie = models.CharField(
        max_length=25,
        choices=TypeRole.choices,
        default=TypeRole.BAILLEUR,
    )
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, blank=True, null=True
    )
    administration = models.ForeignKey(
        "instructeurs.Administration", on_delete=models.CASCADE, blank=True, null=True
    )
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False)
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE, null=False)

    def __str__(self):
        entity = ""
        if self.bailleur is not None:
            entity = self.bailleur
        elif self.administration is not None:
            entity = self.administration

        return f"{self.user} - {self.typologie} - {entity}"
