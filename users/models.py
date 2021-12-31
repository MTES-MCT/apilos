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


class User(AbstractUser):
    cerbere_uid = models.IntegerField(null=True)

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
        return self.is_role(TypeRole.BAILLEUR) or self.is_superuser

    def is_instructeur(self):
        return self.is_role(TypeRole.INSTRUCTEUR) or self.is_superuser

    def is_role(self, role):
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
            administration_ids = list(
                map(
                    lambda role: role.administration_id,
                    self.role_set.filter(typologie=TypeRole.INSTRUCTEUR),
                )
            )
            return {prefix + "administration_id__in": administration_ids}

        if self.is_bailleur():
            bailleur_ids = list(
                map(
                    lambda role: role.bailleur_id,
                    self.role_set.filter(typologie=TypeRole.BAILLEUR),
                )
            )
            return {prefix + "bailleur_id__in": bailleur_ids}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permattant le filtre sur les programmes"
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
            administration_ids = list(
                map(
                    lambda role: role.administration_id,
                    self.role_set.filter(typologie=TypeRole.INSTRUCTEUR),
                )
            )
            return {"id__in": administration_ids}

        # to do : manage programme related to geo for bailleur
        if self.is_bailleur():
            return {}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permattant le "
            + "filtre sur les administrations"
        )

    def administrations(self):
        return Administration.objects.filter(**self.administration_filter())

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
            return {}

        if self.is_bailleur():
            bailleur_ids = list(
                map(
                    lambda role: role.bailleur_id,
                    self.role_set.filter(typologie=TypeRole.BAILLEUR),
                )
            )
            return {"id__in": bailleur_ids}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permattant le filtre sur les bailleurs"
        )

    def bailleurs(self):
        return Bailleur.objects.filter(**self.bailleur_filter())

    def convention_filter(self):
        if self.is_superuser:
            return {}

        # to do : manage programme related to geo for instructeur
        if self.is_instructeur():
            administration_ids = list(
                map(
                    lambda role: role.administration_id,
                    self.role_set.filter(typologie=TypeRole.INSTRUCTEUR),
                )
            )
            return {"programme__administration_id__in": administration_ids}

        if self.is_bailleur():
            bailleur_ids = list(
                map(
                    lambda role: role.bailleur_id,
                    self.role_set.filter(typologie=TypeRole.BAILLEUR),
                )
            )
            return {"bailleur_id__in": bailleur_ids}

        raise PermissionDenied(
            "L'utilisateur courant n'a pas de role associé permattant le filtre sur les bailleurs"
        )

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
