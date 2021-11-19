from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.db import models

from conventions.models import Convention, ConventionStatut
from programmes.models import Lot

from users.type_models import TypeRole


class slist(list):
    @property
    def length(self):
        return len(self)


class User(AbstractUser):
    def _has_view_convention(self, obj):
        if isinstance(obj, Convention):
            # is bailleur of the convention or is instructeur of the convention
            return self.role_set.filter(
                bailleur_id=obj.bailleur_id
            ) or self.role_set.filter(administration_id=obj.programme.administration_id)
        raise Exception(
            "Les permissions ne sont pas correctement configurer, un "
            + "objet de type Convention doit être asocié à la "
            + "permission 'view_convention'"
        )

    def _has_change_convention(self, obj):
        if isinstance(obj, Convention):
            if (
                # is bailleur of the convention
                self.role_set.filter(bailleur_id=obj.bailleur_id)
                # is instructeur of the convention
                or self.role_set.filter(
                    administration_id=obj.programme.administration_id
                )
            ):
                return obj.statut != ConventionStatut.CLOS
            return False
        raise Exception(
            "Les permissions ne sont pas correctement configurer, un "
            + "objet de type Convention doit être asocié à la "
            + "permission 'change_convention'"
        )

    def has_perm(self, perm, obj=None):
        if self.is_staff:
            return True
        # request.user.check_perm("convention.change_convention", convention)
        if perm == "convention.change_convention":
            return self._has_change_convention(obj)
        # request.user.check_perm("convention.add_convention", lot)
        if perm == "convention.add_convention":
            if isinstance(obj, Lot):
                # is bailleur of the convention or is instructeur of the convention
                return self.role_set.filter(
                    bailleur_id=obj.bailleur_id
                ) or self.role_set.filter(
                    administration_id=obj.programme.administration_id
                )
        # request.user.check_perm("convention.view_convention", convention)
        if perm == "convention.view_convention":
            return self._has_view_convention(obj)

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
        return self.is_role(TypeRole.BAILLEUR)

    def is_instructeur(self):
        return self.is_role(TypeRole.INSTRUCTEUR) or self.is_staff

    def is_role(self, role):
        return role in map(lambda r: r.typologie, self.role_set.all())

    def programme_filter(self):
        bailleur_ids = list(
            map(
                lambda role: role.bailleur_id,
                self.role_set.filter(typologie=TypeRole.BAILLEUR),
            )
        )
        if bailleur_ids:
            return {"bailleur_id__in": bailleur_ids}
        return {}

    def bailleurs(self):
        return slist(
            map(
                lambda role: role.bailleur,
                self.role_set.filter(typologie=TypeRole.BAILLEUR),
            )
        )

    def convention_filter(self):
        bailleur_ids = list(
            map(
                lambda role: role.bailleur_id,
                self.role_set.filter(typologie=TypeRole.BAILLEUR),
            )
        )
        administration_ids = list(
            map(
                lambda role: role.administration_id,
                self.role_set.filter(typologie=TypeRole.INSTRUCTEUR),
            )
        )
        filter_result = {}
        if administration_ids:
            filter_result["programme__administration_id__in"] = administration_ids
        if bailleur_ids:
            filter_result["bailleur_id__in"] = bailleur_ids
        return filter_result

    def full_editable_convention(self, convention):
        # is bailleur of the convention
        if self.role_set.filter(bailleur_id=convention.bailleur_id):
            return convention.statut == ConventionStatut.BROUILLON
        # is instructeur of the convention
        if self.role_set.filter(
            administration_id=convention.programme.administration_id
        ):
            return convention.statut == ConventionStatut.INSTRUCTION
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
