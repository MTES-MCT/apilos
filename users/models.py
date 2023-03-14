import logging

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.functions import Substr
from django.forms.models import model_to_dict
from simple_history.models import HistoricalRecords

from apilos_settings.models import Departement
from bailleurs.models import Bailleur
from conventions.models import Convention, ConventionStatut
from instructeurs.models import Administration
from programmes.models import Lot, Programme
from users.type_models import TypeRole, EmailPreferences

logger = logging.getLogger(__name__)


class GroupProfile(models.TextChoices):
    STAFF = "STAFF", "Staff"
    BAILLEUR = "BAILLEUR", "Bailleur"
    INSTRUCTEUR = "INSTRUCTEUR", "Instructeur"
    SIAP_ADM_CENTRALE = "ADM_CENTRALE", "Administration Centrale"
    SIAP_DIR_REG = "DIR_REG", "Service régional"
    SIAP_SER_DEP = "SER_DEP", "Service départemental"
    SIAP_SER_GEST = "SER_GEST", "Service de gestion - délégataire des aides à la pierre"
    SIAP_ASS_HLM = "ASS_HLM", "Association HLM"
    SIAP_MO_PERS_MORALE = "MO_PERS_MORALE", "Maitre d'ouvrage - personne morale"
    SIAP_MO_PERS_PHYS = "MO_PERS_PHYS", "Maitre d'ouvrage - personne physique"

    @classmethod
    def instructeur_profiles(cls):
        return [
            GroupProfile.STAFF,
            GroupProfile.INSTRUCTEUR,
            GroupProfile.SIAP_SER_GEST,
            GroupProfile.SIAP_ADM_CENTRALE,
            GroupProfile.SIAP_DIR_REG,
            GroupProfile.SIAP_SER_DEP,
        ]

    @classmethod
    def bailleur_profiles(cls):
        return [
            GroupProfile.STAFF,
            GroupProfile.BAILLEUR,
            GroupProfile.SIAP_MO_PERS_MORALE,
            GroupProfile.SIAP_MO_PERS_PHYS,
        ]


class User(AbstractUser):
    # pylint: disable=R0904
    siap_habilitation = {}
    administrateur_de_compte = models.BooleanField(default=False)
    telephone = models.CharField(
        null=True,
        max_length=25,
    )
    cerbere_login = models.CharField(
        null=True,
        max_length=255,
    )
    preferences_email = models.CharField(
        max_length=25,
        choices=EmailPreferences.choices,
        default=EmailPreferences.PARTIEL,
    )
    filtre_departements = models.ManyToManyField(
        Departement,
        related_name="filtre_departements",
        # label="Filtrer par départements",
        help_text=(
            "Les programmes et conventions affichés à l'utilisateur seront filtrés en utilisant"
            + " la liste des départements ci-dessous"
        ),
        blank=True,
    )
    creator = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, blank=True, null=True
    )
    history = HistoricalRecords(excluded_fields=["last_login"])
    read_popup = models.BooleanField(default=False)

    def has_object_permission(self, obj):
        if isinstance(obj, (Convention, Lot)):
            if (
                "role" in self.siap_habilitation
                and self.siap_habilitation["role"]["typologie"]
                == TypeRole.ADMINISTRATEUR
            ):

                if self.siap_habilitation["role"]["perimetre_departement"]:
                    return (
                        obj.programme.code_insee_departement
                        == self.siap_habilitation["role"]["perimetre_departement"]
                    )
                if self.siap_habilitation["role"]["perimetre_region"]:
                    return (
                        obj.programme.code_insee_region
                        == self.siap_habilitation["role"]["perimetre_region"]
                    )
                return True

            # Get bailleur and its parent to know if the user has rights on one of those
            bailleur = Bailleur.objects.prefetch_related("parent").get(
                id=obj.programme.bailleur_id
            )
            bailleur_ids = [obj.programme.bailleur_id]
            if bailleur.parent:
                bailleur_ids.append(bailleur.parent.id)
            # is bailleur of the convention or is instructeur of the convention
            return self.roles.filter(bailleur_id__in=bailleur_ids) or self.roles.filter(
                administration_id=obj.programme.administration_id
            )
        raise Exception(
            "Les permissions ne sont pas correctement configurer, un "
            + "objet de type Convention doit être asocié à la "
            + "permission 'change_convention'"
        )

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        # check object permission
        if obj is not None and not self.has_object_permission(obj):
            return False
        # check permission itself
        permissions = []
        for role in self.roles.all():
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
        if self.is_cerbere_user():
            return "currently" in self.siap_habilitation and self.siap_habilitation[
                "currently"
            ] in [GroupProfile.SIAP_MO_PERS_MORALE, GroupProfile.SIAP_MO_PERS_PHYS]
        if bailleur_id is not None:
            return self.roles.filter(bailleur_id=bailleur_id)
        return self._is_role(TypeRole.BAILLEUR) or self.is_superuser

    def get_active_bailleurs(self):
        return (
            self.roles.filter(typologie=TypeRole.BAILLEUR)
            .values_list("bailleur", flat=True)
            .distinct()
        )

    def is_instructeur(self):
        if self.is_cerbere_user():
            return "currently" in self.siap_habilitation and self.siap_habilitation[
                "currently"
            ] in [
                GroupProfile.SIAP_SER_GEST,
                GroupProfile.SIAP_DIR_REG,
                GroupProfile.SIAP_SER_DEP,
                GroupProfile.SIAP_ADM_CENTRALE,
            ]
        return self._is_role(TypeRole.INSTRUCTEUR) or self.is_superuser

    def get_active_administrations(self):
        return (
            self.roles.filter(typologie=TypeRole.INSTRUCTEUR)
            .values_list("administration", flat=True)
            .distinct()
        )

    def is_administration(self):
        if self.is_cerbere_user():
            return "currently" in self.siap_habilitation and self.siap_habilitation[
                "currently"
            ] in [
                GroupProfile.SIAP_DIR_REG,
                GroupProfile.SIAP_ADM_CENTRALE,
            ]
        return self._is_role(TypeRole.INSTRUCTEUR) or self.is_superuser

    def _is_role(self, role):
        return role in map(lambda r: r.typologie, self.roles.all())

    def programmes(self) -> list:
        """
        Programme of the user following is role :
        * super admin = all programme, filtre = {}
        * instructeur = all programme following geo, filtre = {}
        * bailleur = programme which belongs to the bailleurs, filtre = {bailleur_id__in: [x,y,z]}
        else raise
        """
        if self.is_superuser:
            return Programme.objects.all()

        if self.is_instructeur():
            return Programme.objects.filter(
                administration_id__in=self.administration_ids()
            )

        if self.is_bailleur():
            programmes_result = Programme.objects.filter(
                bailleur_id__in=self._bailleur_ids()
            )
            if self.filtre_departements.exists():
                programmes_result = programmes_result.annotate(
                    departement=Substr("code_postal", 1, 2)
                ).filter(
                    departement__in=list(
                        self.filtre_departements.all().values_list(
                            "code_postal", flat=True
                        )
                    )
                )
            return programmes_result

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permettant le filtre sur les programmes"
        )

    def lots(self):
        """
        Lots of the user following is role :
        * super admin = all lots
        * instructeur = all lots of programme which belong to its administrations
        * bailleur = all lots which belongs to its bailleur entities
        else raise
        """
        return Lot.objects.filter(programme__in=self.programmes())

    #
    # list of administration following role
    # super admin = all administration, filtre = {}
    # instructeur = ???, filtre = {}
    # bailleur = ???, filtre = {}
    # else raise
    #
    def administration_filter(self, full_scope=False):
        if self.is_superuser:
            return {}

        # to do : manage programme related to geo for instructeur
        if self.is_instructeur():
            return {"id__in": self.administration_ids()}

        # to do : manage programme related to geo for bailleur
        if self.is_bailleur():
            if full_scope:
                return {}
            return {"id__in": []}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permettant le "
            + "filtre sur les administrations"
        )

    def administration_ids(self):
        if self.is_cerbere_user():
            if "administration" in self.siap_habilitation:
                return [self.siap_habilitation["administration"]["id"]]
            return None

        return list(
            map(
                lambda role: role.administration_id,
                self.roles.filter(typologie=TypeRole.INSTRUCTEUR),
            )
        )

    def administrations(self, order_by="nom", full_scope=False):
        return Administration.objects.filter(
            **self.administration_filter(full_scope=full_scope)
        ).order_by(order_by)

    #
    # list of bailleurs following role
    # super admin = all bailleurs, filtre = {}
    # instructeur = all bailleurs following geo, filtre = {}
    # bailleur = bailleurs which belongs to the user as a bailleur, filtre = {id__in: [x,y,z]}
    # else raise
    #
    def bailleur_filter(self, full_scope=False):
        if self.is_superuser:
            return {}

        # to do : manage programme related to geo for instructeur
        if self.is_instructeur():
            if full_scope:
                return {}
            return {"id__in": []}

        if self.is_bailleur():
            return {"id__in": self._bailleur_ids()}

        raise Exception(
            "L'utilisateur courant n'a pas de role associé permettant le filtre sur les bailleurs"
        )

    def _bailleur_ids(self) -> list:
        if self.is_cerbere_user():
            return [self.siap_habilitation["bailleur"]["id"]]

        bailleur_ids = list(
            map(
                lambda role: role.bailleur_id,
                self.roles.filter(typologie=TypeRole.BAILLEUR),
            )
        )
        bailleur_ids.extend(
            [
                bailleur.id
                for bailleur in Bailleur.objects.filter(parent_id__in=bailleur_ids)
            ]
        )

        return bailleur_ids

    def bailleurs(self, order_by="nom", full_scope=False):
        return Bailleur.objects.filter(
            **self.bailleur_filter(full_scope=full_scope)
        ).order_by(order_by)

    def _apply_geo_filters(self, conventions):
        if self.is_cerbere_user() and "role" in self.siap_habilitation:
            if self.siap_habilitation["role"]["perimetre_departement"]:
                return conventions.filter(
                    programme__code_insee_departement=self.siap_habilitation["role"][
                        "perimetre_departement"
                    ]
                )
            if self.siap_habilitation["role"]["perimetre_region"]:
                return conventions.filter(
                    programme__code_insee_region=self.siap_habilitation["role"][
                        "perimetre_region"
                    ]
                )
        return conventions

    def _apply_administration_ids_filters(self, convs):
        administrations_ids = self.administration_ids()
        if administrations_ids:
            convs = convs.filter(
                programme__administration_id__in=self.administration_ids(),
            )
        return convs

    def conventions(self, active: bool | None = None):
        """
        Return the conventions the user has right to view.
        For an `instructeur`, it returns the conventions of its administrations
        For a `bailleur`, it returns the conventions of its bailleur entities in the limit of its
        geographic filter.

        The active argument allows to filter this list based on the status of the convention,
        whether it's active (A_SIGNER and below) or completed (SIGNEE and up).
        If omitted or None, no filter is applied
        """
        convs = Convention.objects
        if active is not None:
            convs = convs.filter(
                statut__in=ConventionStatut.active_statuts()
                if active
                else ConventionStatut.completed_statuts()
            )

        if self.is_superuser:
            return convs.all()
        if (
            self.is_cerbere_user()
            and "role" in self.siap_habilitation
            and self.siap_habilitation["role"]["typologie"] == TypeRole.ADMINISTRATEUR
        ):
            return self._apply_geo_filters(convs)

        if self.is_instructeur():
            convs = self._apply_geo_filters(convs)
            convs = self._apply_administration_ids_filters(convs)
            return convs

        if self.is_bailleur():
            convs = self._apply_geo_filters(convs)
            convs = convs.filter(programme__bailleur_id__in=self._bailleur_ids())
            if self.id and self.filtre_departements.exists():
                convs = convs.annotate(
                    departement=Substr("programme__code_postal", 1, 2)
                ).filter(
                    departement__in=list(
                        self.filtre_departements.all().values_list(
                            "code_postal", flat=True
                        )
                    )
                )
            return convs

        raise PermissionDenied(
            "L'utilisateur courant n'a pas de role associé permettant le filtre sur les bailleurs"
        )

    def user_list(self, order_by="username"):
        if self.is_superuser:
            return User.objects.all().order_by(order_by)
        if self.is_bailleur():
            return (
                User.objects.all()
                .filter(roles__bailleur_id__in=self._bailleur_ids())
                .order_by(order_by)
                .distinct()
            )
        if self.is_instructeur():
            return (
                User.objects.all()
                .filter(roles__administration_id__in=self.administration_ids())
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

    def is_cerbere_user(self):
        return self.cerbere_login is not None

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name}".strip()
            if self.first_name or self.last_name
            else self.username
        )


class Role(models.Model):
    class Meta:
        unique_together = ("typologie", "bailleur", "administration", "user")

    id = models.AutoField(primary_key=True)
    typologie = models.CharField(
        max_length=25,
        choices=TypeRole.choices,
        default=TypeRole.BAILLEUR,
    )
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur",
        blank=True,
        related_name="roles",
        null=True,
        on_delete=models.CASCADE,
    )
    administration = models.ForeignKey(
        "instructeurs.Administration",
        blank=True,
        related_name="roles",
        null=True,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "users.User",
        related_name="roles",
        null=False,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        "auth.Group",
        related_name="roles",
        null=False,
        on_delete=models.CASCADE,
    )
    perimetre_region = models.CharField(max_length=10, null=True)
    perimetre_departement = models.CharField(max_length=10, null=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        logger.info(
            "created Role %s for user %s ",
            model_to_dict(self),
            model_to_dict(self.user),
        )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logger.info(
            "removed Role %s for user %s ",
            model_to_dict(self),
            model_to_dict(self.user),
        )
        return super().delete(*args, **kwargs)

    def __str__(self):
        entity = ""
        if self.bailleur is not None:
            entity = self.bailleur
        elif self.administration is not None:
            entity = self.administration

        return f"{self.user} - {self.typologie} - {entity}"
