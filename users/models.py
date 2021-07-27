from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    pass

# To implement if we need to custom permission
    def has_perm(self, perm, obj=None):
        #print(f'PERMISSION : {perm}')
        if self.is_staff:
            return True
        permissions = []
        for role in self.role_set.all():
            permissions += map(lambda permission: permission.content_type.name + '.' + permission.codename, role.group.permissions.all())
        return perm in permissions

    def is_bailleur(self):
        return self.is_role(Role.TypeRole.BAILLEUR)

    def is_instructeur(self):
        return self.is_role(Role.TypeRole.INSTRUCTEUR)

    def is_role(self, role):
        return role in map( lambda r : r.typologie, self.role_set.all())

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Role(models.Model):
    class TypeRole(models.TextChoices):
        INSTRUCTEUR = "INSTRUCTEUR", "Instructeur"
        BAILLEUR = "BAILLEUR", "Bailleur"
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
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=False
    )
    group = models.ForeignKey(
        "auth.Group", on_delete=models.CASCADE, null=False
    )

    def __str__(self):
        entity = ''
        if self.bailleur is not None:
            entity = self.bailleur
        elif self.administration is not None:
            entity = self.administration

        return f"{self.typologie} - {entity}"
