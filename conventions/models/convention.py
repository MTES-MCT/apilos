import datetime
import logging
import uuid
from collections import defaultdict
from datetime import date
from itertools import chain

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Prefetch, Q
from django.forms import model_to_dict
from django.http import HttpRequest
from django.utils.functional import cached_property
from waffle import switch_is_active

from conventions.models import TypeEvenement
from conventions.models.avenant_type import AvenantType
from conventions.models.choices import ConventionStatut, ConventionType1and2
from conventions.models.convention_history import ConventionHistory
from ecoloweb.models import EcoloReference
from programmes.models import Financement, LocauxCollectifs, Lot, TypeStationnement
from users.type_models import EmailPreferences, TypeRole

logger = logging.getLogger(__name__)


class ConventionGroupingError(Exception):
    pass


class ConventionQuerySet(models.QuerySet):
    def avenants(self):
        return self.exclude(parent=None)

    def without_denonciation_and_resiliation(self):
        return self.exclude(avenant_types__nom__in=["denonciation", "resiliation"])


class ConventionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(Prefetch("lots", queryset=Lot.objects.order_by("pk")))
        )

    def _split_first_convention(self, conventions):
        """Returns the first convention and the rest of the conventions separately."""
        if not switch_is_active(settings.SWITCH_CONVENTION_MIXTE_ON):
            return

        all_conventions = list(conventions.all())
        if not all_conventions:
            return None, []
        return all_conventions[0], all_conventions[1:]

    def group_conventions(self, uuids_conventions):
        if not switch_is_active(settings.SWITCH_CONVENTION_MIXTE_ON):
            return

        if not uuids_conventions:
            raise ConventionGroupingError(
                "We can't create a mixte convention, a list of uuids conventions must be provided"
            )

        related_conventions = self.model.objects.filter(uuid__in=uuids_conventions)

        programme_ids = {conv.programme_id for conv in related_conventions}
        if len(programme_ids) > 1:
            raise ConventionGroupingError("Conventions must be from the same programme")

        statut_list = {conv.statut for conv in related_conventions}
        if statut_list != {ConventionStatut.PROJET.label}:
            raise ConventionGroupingError("Conventions must be in the same status")

        type_habitat_list = {
            conv.lots.first().type_habitat for conv in related_conventions
        }
        if len(type_habitat_list) > 1:
            raise ConventionGroupingError(
                "All lots in the conventions must have the same type of habitat"
            )

        for conv in related_conventions:
            if conv.is_avenant():
                raise ConventionGroupingError("Avenants cannot be grouped")

        convention, others_conventions = self._split_first_convention(
            related_conventions
        )
        convention.set_lots(others_conventions)

        return convention.programme, convention.lots, convention

    def _degroup_convention(self, convention):
        if not switch_is_active(settings.SWITCH_CONVENTION_MIXTE_ON):
            return
        degrouped_conventions_ids = []
        if convention.is_mixte:
            for lot in convention.lots.all():
                degrouped_convention = convention.clone_convention()
                lot.convention = degrouped_convention
                lot.save()
                degrouped_conventions_ids.append(degrouped_convention.id)
            if degrouped_conventions_ids:
                convention.delete()

        return self.model.objects.filter(id__in=degrouped_conventions_ids)

    def degroup_conventions(self, list_of_uuids_conventions):
        if not switch_is_active(settings.SWITCH_CONVENTION_MIXTE_ON):
            return

        if not list_of_uuids_conventions:
            raise ConventionGroupingError(
                "We can't degroup convention, UUIDs list is required"
            )

        related_conventions = self.model.objects.filter(
            uuid__in=list_of_uuids_conventions
        )

        if any(conv.has_avenant for conv in related_conventions):
            raise ConventionGroupingError("Conventions must not have any avenant")

        statut_list = {conv.statut for conv in related_conventions}
        if statut_list != {ConventionStatut.PROJET.label}:
            raise ConventionGroupingError("Conventions must be in the same status")

        for conv in related_conventions:
            if conv.is_avenant():
                raise ConventionGroupingError("Avenants cannot be degrouped")

        return self._degroup_convention(related_conventions.first())


class Convention(models.Model):
    objects = ConventionManager.from_queryset(ConventionQuerySet)()

    class Meta:
        indexes = [
            models.Index(fields=["numero"], name="convention_numero_idx"),
            models.Index(
                fields=["numero_pour_recherche"], name="convention_num_for_search_idx"
            ),
            models.Index(fields=["statut"], name="convention_statut_idx"),
            models.Index(fields=["uuid"], name="convention_uuid_idx"),
            models.Index(fields=["valide_le"], name="convention_valid_le_idx"),
            models.Index(
                fields=["televersement_convention_signee_le"],
                name="convention_tele_signee_le_idx",
            ),
            models.Index(fields=["cree_le"], name="convention_cree_le_idx"),
        ]
        # constraints = [
        #     # https://github.com/betagouv/SPPNautInterface/issues/227
        #     models.UniqueConstraint(
        #         fields=["programme_id", "lot_id", "financement"],
        #         condition=models.Q(
        #             statut__in=[
        #                 ConventionStatut.PROJET.label,
        #                 ConventionStatut.INSTRUCTION.label,
        #                 ConventionStatut.CORRECTION.label,
        #                 ConventionStatut.A_SIGNER.label,
        #                 ConventionStatut.SIGNEE.label,
        #             ]
        #         ),
        #         name="unique_display_name",
        #     )
        # ]

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="avenants",
    )
    numero = models.CharField(max_length=255, null=True, blank=True)
    numero_pour_recherche = models.CharField(max_length=255, null=True, blank=True)
    programme = models.ForeignKey(
        "programmes.Programme",
        related_name="conventions",
        on_delete=models.CASCADE,
        null=False,
    )

    date_fin_conventionnement = models.DateField(null=True, blank=True)

    # fix me: weird to keep fond_propre here
    fond_propre = models.FloatField(null=True, blank=True)
    commentaires = models.TextField(null=True, blank=True)
    attached = models.TextField(null=True, blank=True)
    statut = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET.label,
    )
    soumis_le = models.DateTimeField(null=True, blank=True)
    premiere_soumission_le = models.DateTimeField(null=True, blank=True)
    valide_le = models.DateField(null=True, blank=True)
    cree_par = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)
    type1and2 = models.CharField(
        max_length=25, choices=ConventionType1and2.choices, null=True, blank=True
    )
    type2_lgts_concernes_option1 = models.BooleanField(default=True)
    type2_lgts_concernes_option2 = models.BooleanField(default=True)
    type2_lgts_concernes_option3 = models.BooleanField(default=True)
    type2_lgts_concernes_option4 = models.BooleanField(default=True)
    type2_lgts_concernes_option5 = models.BooleanField(default=True)
    type2_lgts_concernes_option6 = models.BooleanField(default=True)
    type2_lgts_concernes_option7 = models.BooleanField(default=True)
    type2_lgts_concernes_option8 = models.BooleanField(default=True)
    avenant_types = models.ManyToManyField(
        AvenantType,
        blank=True,
        max_length=50,
        related_name="conventions",
        verbose_name="Type d'avenant",
    )
    signataire_nom = models.CharField(max_length=255, null=True, blank=True)
    signataire_fonction = models.CharField(max_length=255, null=True, blank=True)
    signataire_date_deliberation = models.DateField(null=True, blank=True)
    signataire_bloc_signature = models.CharField(max_length=5000, null=True, blank=True)

    # Champs liés au SPF (Service de Publication Foncière))
    date_publication_spf = models.DateField(null=True, blank=True)
    reference_spf = models.CharField(max_length=50, null=True)
    date_envoi_spf = models.DateField(null=True, blank=True)
    date_refus_spf = models.DateField(null=True)
    motif_refus_spf = models.CharField(max_length=1000, null=True)
    # Missing option for :

    # Gestionnaire data are needed for FOYER (AND RESIDENCE)
    gestionnaire = models.CharField(max_length=255, null=True, blank=True)
    gestionnaire_signataire_nom = models.CharField(
        max_length=255, null=True, blank=True
    )
    gestionnaire_signataire_fonction = models.CharField(
        max_length=255, null=True, blank=True
    )
    gestionnaire_signataire_date_deliberation = models.DateField(null=True, blank=True)
    gestionnaire_signataire_bloc_signature = models.CharField(
        max_length=5000, null=True, blank=True
    )
    gestionnaire_bloc_info_complementaire = models.CharField(
        max_length=5000, null=True, blank=True
    )

    donnees_validees = models.TextField(null=True, blank=True)
    nom_fichier_signe = models.CharField(max_length=255, null=True, blank=True)
    nom_fichier_publication_spf = models.CharField(
        max_length=255, null=True, blank=True
    )
    televersement_convention_signee_le = models.DateField(null=True, blank=True)
    desc_avenant = models.TextField(null=True, blank=True)

    historique_financement_public = models.CharField(
        null=True, blank=True, max_length=5000
    )

    attribution_agees_autonomie = models.BooleanField(default=False)
    attribution_agees_ephad = models.BooleanField(default=False)
    attribution_agees_desorientees = models.BooleanField(default=False)
    attribution_agees_petite_unite = models.BooleanField(default=False)
    attribution_agees_autre = models.BooleanField(default=False)
    attribution_agees_autre_detail = models.CharField(
        max_length=255, null=True, blank=True
    )
    attribution_handicapes_foyer = models.BooleanField(default=False)
    attribution_handicapes_foyer_de_vie = models.BooleanField(default=False)
    attribution_handicapes_foyer_medicalise = models.BooleanField(default=False)
    attribution_handicapes_autre = models.BooleanField(default=False)
    attribution_handicapes_autre_detail = models.CharField(
        max_length=255, null=True, blank=True
    )
    attribution_inclusif_conditions_specifiques = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_inclusif_conditions_admission = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_inclusif_modalites_attribution = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_inclusif_partenariats = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_inclusif_activites = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_reservation_prefectorale = models.IntegerField(null=True, blank=True)
    attribution_modalites_reservations = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_modalites_choix_personnes = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_prestations_integrees = models.CharField(
        null=True, blank=True, max_length=50000
    )
    attribution_prestations_facultatives = models.CharField(
        null=True, blank=True, max_length=50000
    )

    foyer_residence_variante_1 = models.BooleanField(default=True)
    foyer_residence_variante_2 = models.BooleanField(default=True)
    foyer_residence_variante_2_travaux = models.CharField(
        null=True, blank=True, max_length=5000
    )
    foyer_residence_variante_2_nb_annees = models.IntegerField(null=True, blank=True)
    foyer_residence_variante_2_nb_tranches = models.IntegerField(null=True, blank=True)

    foyer_residence_variante_3 = models.BooleanField(default=True)

    attribution_residence_sociale_ordinaire = models.BooleanField(default=False)
    attribution_pension_de_famille = models.BooleanField(default=False)
    attribution_residence_accueil = models.BooleanField(default=False)

    champ_libre_avenant = models.TextField(null=True, blank=True)

    date_denonciation = models.DateField(null=True, blank=True)
    motif_denonciation = models.TextField(null=True, blank=True)
    fichier_instruction_denonciation = models.TextField(null=True, blank=True)

    date_resiliation = models.DateField(null=True, blank=True)
    motif_resiliation = models.TextField(null=True, blank=True)
    fichier_instruction_resiliation = models.TextField(null=True, blank=True)

    adresse = models.TextField(null=True, blank=True)

    fichier_override_cerfa = models.TextField(null=True, blank=True)

    identification_bailleur = models.BooleanField(default=False)
    identification_bailleur_detail = models.TextField(null=True, blank=True)

    @property
    def lot(self) -> Lot:
        return self.lots.first()

    @property
    def lots(self) -> Lot:
        return self.lots

    @property
    def is_mixte(self) -> bool:
        """
        Returns True if the convention has multiple lots (mixte),
        False if it has only one lot (Simple).
        """
        return self.lots.count() > 1

    @property
    def is_pls_financement_type(self) -> bool:
        return self.lot.is_pls_financement_type

    @property
    def attribution_type(self) -> str | None:
        if not self.programme.is_foyer:
            return None

        if (
            self.attribution_agees_autonomie
            or self.attribution_agees_ephad
            or self.attribution_agees_desorientees
            or self.attribution_agees_petite_unite
            or self.attribution_agees_autre
        ):
            return "agees"

        if (
            self.attribution_handicapes_foyer
            or self.attribution_handicapes_foyer_de_vie
            or self.attribution_handicapes_foyer_medicalise
            or self.attribution_handicapes_autre
        ):
            return "handicapes"

        return "inclusif"

    # Needed for admin
    @property
    def administration(self):
        return self.programme.administration

    @property
    def bailleur(self):
        return self.programme.bailleur

    @property
    def lots_list(self):
        from django.utils.html import format_html_join

        lots = self.lots.all()  # use related_name if set in Lot model
        return format_html_join(
            ", ",
            '<a href="/admin/programmes/lot/{}/change/">{}</a>',
            ((lot.pk, str(lot)) for lot in lots),
        )

    @property
    def get_financement_display(self):
        return ", ".join(
            [str(lot.get_financement_display()) for lot in self.lots.all()]
        )

    @property
    def nb_logements(self):
        return sum([lot.nb_logements for lot in self.lots.all() if lot.nb_logements])

    @cached_property
    def ecolo_reference(self) -> EcoloReference | None:
        if self.id is not None:
            return EcoloReference.objects.filter(
                apilos_model="conventions.Convention", apilos_id=self.id
            ).first()

        return None

    def __str__(self):
        str_compose = []
        if programme := self.programme:
            str_compose.append(programme.ville)
            str_compose.append(programme.nom)
        if lots := self.lots.all():
            for lot in lots:
                str_compose.append(f"{lot.nb_logements} lgts")
                str_compose.append(lot.get_type_habitat_display())
                str_compose.append(lot.financement)
        if not str_compose:
            str_compose.append(self.uuid)
        return " - ".join(str_compose)

    def is_bailleur_editable(self):
        return self.statut in (
            ConventionStatut.PROJET.label,
            ConventionStatut.CORRECTION.label,
        )

    def get_comments_dict(self):
        result = {}
        for comment in self.comment_set.all().order_by("cree_le"):
            comment_name = (
                comment.nom_objet
                + "__"
                + comment.champ_objet
                + "__"
                + str(comment.uuid_objet)
            )
            if comment_name not in result:
                result[comment_name] = []
            result[comment_name].append(comment)
        return result

    def _get_last_notification_by_role(self, role: TypeRole):
        try:
            return (
                self.conventionhistories.prefetch_related("user")
                .prefetch_related("user__roles")
                .filter(
                    statut_convention__in=[
                        ConventionStatut.INSTRUCTION.label,
                        ConventionStatut.CORRECTION.label,
                    ],
                    user__roles__typologie=role,
                )
                .latest("cree_le")
            )
        except ConventionHistory.DoesNotExist:
            return None

    def get_last_bailleur_notification(self):
        return self._get_last_notification_by_role(TypeRole.BAILLEUR)

    def get_last_instructeur_notification(self):
        return self._get_last_notification_by_role(TypeRole.INSTRUCTEUR)

    def get_last_avenant_or_parent(self):
        if not self.parent:
            return None

        last_avenant_or_parent = self.parent

        if last_avenant_or_parent.avenants.count() > 1:
            last_avenant_or_parent = last_avenant_or_parent.avenants.all().order_by(
                "-cree_le"
            )[1]
        return last_avenant_or_parent

    @property
    def has_avenant(self):
        return self.avenants.exists()

    def get_email_bailleur_users(self):
        """
        return the email of the bailleurs to send them an email following their email
         preferences
        partial should include only the bailleur which interact with the convention
        using convention statut
        """
        users_partial = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.conventionhistories.prefetch_related("user").filter(
                        user__preferences_email=EmailPreferences.PARTIEL,
                        user__roles__typologie=TypeRole.BAILLEUR,
                    ),
                )
            )
        )
        users_all_email = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.programme.bailleur.roles.prefetch_related("user").filter(
                        user__preferences_email=EmailPreferences.TOUS
                    ),
                )
            )
        )
        all_users = list(set(users_partial + users_all_email))
        # TODO : Find a wait to catch when no bailleur is set and ask instructeur to set
        #  one
        return all_users

    def get_email_instructeur_users(self, include_partial: bool = False):
        """
        return the email of the instructeur to send them an email following their email preferences
        if include_partial (in case of a new convention, all instructeurs should be alerted)
        else partial should include only the instucteur which interact with the convention
        using convention statut
        """
        if include_partial:
            # All instructeurs of the administration will be notified except one
            # who choose no email (EmailPreferences.AUCUN)
            return list(
                set(
                    map(
                        lambda x: x.user.email,
                        self.programme.administration.roles.prefetch_related(
                            "user"
                        ).filter(
                            Q(user__preferences_email=EmailPreferences.PARTIEL)
                            | Q(user__preferences_email=EmailPreferences.TOUS)
                        ),
                    )
                )
            )
        users_partial = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.conventionhistories.prefetch_related("user").filter(
                        user__preferences_email=EmailPreferences.PARTIEL,
                        user__roles__typologie=TypeRole.INSTRUCTEUR,
                    ),
                )
            )
        )
        users_all_email = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.programme.administration.roles.prefetch_related("user").filter(
                        user__preferences_email=EmailPreferences.TOUS
                    ),
                )
            )
        )
        return users_partial + users_all_email

    def get_convention_prefix(self):
        dept_code = self.programme.code_insee_departement
        admin_code = (
            "D"
            if self.programme.administration.code.startswith("D")
            else self.programme.administration.code
        )
        year = datetime.date.today().year

        convention_numbers_in_year = (
            Convention.objects.filter(
                numero__startswith=f"{dept_code}.",
                valide_le__year=year,
            )
            .exclude(
                statut__in=[
                    ConventionStatut.PROJET,
                    ConventionStatut.INSTRUCTION,
                    ConventionStatut.CORRECTION,
                ],
            )
            .values("numero")
        )

        max_number = 0
        for convention_number in convention_numbers_in_year:
            number = convention_number["numero"].split(".")[-1]
            if number.isdigit() and int(number) > max_number:
                max_number = int(number)

        return f"{dept_code}.{admin_code}.{year%100}.{max_number + 1:04d}"

    def is_avenant(self):
        return self.parent_id is not None

    @cached_property
    def is_denonciation(self):
        return (
            self.parent_id is not None
            and self.avenant_types.filter(nom="denonciation").exists()
        )

    @property
    def is_denonciation_due(self):
        return date.today() > self.date_denonciation

    @cached_property
    def is_resiliation(self) -> bool:
        return (
            self.parent_id is not None
            and self.avenant_types.filter(nom="resiliation").exists()
        )

    @property
    def is_resiliation_due(self):
        return date.today() > self.date_resiliation

    def is_incompleted_avenant_parent(self):
        if self.is_avenant() and (
            not self.parent.programme.ville
            or not self.parent.lot.nb_logements
            or not self.parent.nom_fichier_signe
        ):
            return self
        return None

    def evenement(
        self,
        type_evenement: TypeEvenement,
        description: str = "",
        survenu_le: date | None = None,
    ):
        """
        Déclare un nouvel évènement pour la convention
        """
        # To avoid circular import, refer to Evenement class model via apps.get_model
        apps.get_model("conventions", "Evenement").objects.create(
            convention=self,
            type_evenement=type_evenement,
            survenu_le=survenu_le,
            description=description,
        )

    def journal(self):
        """
        Retourne tous les évènements liés à la convention, par ordre croissant de data d'évènement
        """
        return self.evenements.all().order_by("-survenu_le")

    def statut_for_template(self):
        return {
            "statut": self.statut,
            "statut_display": self.get_statut_display(),
            "key_statut": self.statut[3:].replace(" ", "_").replace("é", "e"),
        }

    def genderize_desc(self, desc):
        if self.is_denonciation:
            return desc.format(pronom="elle", accord="e", article="la", autre="")
        if self.is_avenant():
            return desc.format(pronom="il", accord="", article="le", autre="autre")
        return desc.format(pronom="elle", accord="e", article="la", autre="")

    def short_statut_neutre(self):
        return ConventionStatut.get_by_label(self.statut).neutre

    def short_statut_for_bailleur(self):
        statut = ConventionStatut.get_by_label(self.statut).value.bailleur.label
        return self.genderize_desc(statut)

    def short_statut_for_instructeur(self):
        statut = ConventionStatut.get_by_label(self.statut).value.instructeur.label
        return self.genderize_desc(statut)

    def entete_desc_for_bailleur(self):
        desc = ConventionStatut.get_by_label(
            self.statut
        ).value.bailleur.description_entete
        return self.genderize_desc(desc)

    def entete_desc_for_instructeur(self):
        desc = ConventionStatut.get_by_label(
            self.statut
        ).value.instructeur.description_entete
        return self.genderize_desc(desc)

    def statut_icone(self):
        return ConventionStatut.get_by_label(self.statut).icone

    def mixity_option(self):
        """
        return True if the option regarding the number of lodging in addition to loan to people
        with low revenu should be displayed in the interface and fill in the convention document
        Should be editable when it is a PLUS convention
        """
        return all(
            lot.financement in [Financement.PLUS, Financement.PLUS_CD]
            for lot in self.lots.all()
        )

    def display_not_validated_status(self):
        """
        Text display as Watermark when the convention is in project or instruction status
        """
        if self.statut == ConventionStatut.PROJET.label:
            return "Projet de convention"
        if self.statut in [
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
        ]:
            return "Convention en cours d'instruction"
        return ""

    def clone(self, user, *, convention_origin):
        cloned_programme = self.programme.clone()

        convention_fields = model_to_dict(
            self,
            exclude=[
                "avenant_types",
                "commentaires",
                "cree_le",
                "date_resiliation",
                "donnees_validees",
                "id",
                "mis_a_jour_le",
                "nom_fichier_signe",
                "numero",
                "parent",
                "premiere_soumission_le",
                "programme",
                "soumis_le",
                "televersement_convention_signee_le",
                "valide_le",
                "date_publication_spf",
                "reference_spf",
                "date_envoi_spf",
                "date_refus_spf",
                "motif_refus_spf",
                "nom_fichier_publication_spf",
            ],
        ) | {
            "programme": cloned_programme,
            "parent_id": convention_origin.id,
            "statut": ConventionStatut.PROJET.label,
            "cree_par": user,
        }
        cloned_convention = Convention(**convention_fields)
        cloned_convention.save()

        for lot in self.lots.all():
            lot_fields = model_to_dict(
                lot,
                exclude=[
                    "id",
                    "parent",
                    "convention",
                    "cree_le",
                    "mis_a_jour_le",
                ],
            ) | {
                "parent_id": convention_origin.lot.id,
                "convention": cloned_convention,
            }
            cloned_lot = Lot(**lot_fields)
            cloned_lot.save()

            for logement in lot.logements.all():
                logement.clone(lot=cloned_lot)

            for pret in convention_origin.lot.prets.all():
                pret.clone(lot=cloned_lot)

            for type_stationnement in lot.type_stationnements.all():
                type_stationnement_fields = model_to_dict(
                    type_stationnement,
                    exclude=[
                        "id",
                        "lot",
                        "cree_le",
                        "mis_a_jour_le",
                    ],
                ) | {
                    "lot": cloned_lot,
                }
                cloned_type_stationnement = TypeStationnement(
                    **type_stationnement_fields
                )
                cloned_type_stationnement.save()

            for locaux_collectif in lot.locaux_collectifs.all():
                locaux_collectif_fields = model_to_dict(
                    locaux_collectif,
                    exclude=[
                        "id",
                        "lot",
                        "cree_le",
                        "mis_a_jour_le",
                    ],
                ) | {
                    "lot": cloned_lot,
                }
                cloned_locaux_collectif = LocauxCollectifs(**locaux_collectif_fields)
                cloned_locaux_collectif.save()

        return cloned_convention

    def get_default_convention_number(self):
        if self.is_avenant():
            parent = self.parent
            nb_validated_avenants = parent.avenants.exclude(
                statut__in=[
                    ConventionStatut.PROJET.label,
                    ConventionStatut.INSTRUCTION.label,
                    ConventionStatut.CORRECTION.label,
                ]
            ).count()
            return str(nb_validated_avenants + 1)
        return (
            self.numero
            if self.numero
            else self.get_convention_prefix() if self.programme.administration else ""
        )

    def get_status_definition(self):
        return ConventionStatut.get_by_label(self.statut)

    def cancel(self, request: HttpRequest | None = None):
        if self.statut not in [
            ConventionStatut.PROJET.label,
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
            ConventionStatut.A_SIGNER.label,
        ]:
            return
        previous_status = self.statut
        self.statut = ConventionStatut.ANNULEE.label
        self.save()
        ConventionHistory.objects.create(
            convention=self,
            statut_convention=ConventionStatut.ANNULEE.label,
            statut_convention_precedent=previous_status,
            user=request.user if request else None,
        ).save()

    def resiliation_disabled(self) -> bool:
        return (
            self.fichier_instruction_resiliation is None
            or self.fichier_instruction_resiliation == '{"files": {}, "text": ""}'
        )

    @classmethod
    def date_signature_choices(
        cls, statuts: list[ConventionStatut] | None = None, from_threshold=False
    ) -> list[str]:
        validation_year_threshold = 1900
        if from_threshold:
            earliest = validation_year_threshold
        else:
            qs = Convention.objects.filter(
                televersement_convention_signee_le__isnull=False,
                televersement_convention_signee_le__year__gte=validation_year_threshold,
            )
            if statuts:
                qs = qs.filter(statut__in=[s.label for s in statuts])

            try:
                earliest = qs.earliest(
                    "televersement_convention_signee_le"
                ).televersement_convention_signee_le.year
            except Convention.DoesNotExist:
                earliest = validation_year_threshold  # fallback value

        years = range(date.today().year, earliest - 1, -1)
        return [(year, str(year)) for year in years]

    def get_contributors(self):
        result = {"instructeurs": [], "bailleurs": []}
        user_ids = self.conventionhistories.values_list("user_id", flat=True).distinct()
        # get_user_model is used to avoid circular imports
        user_model = get_user_model()
        for user_id in user_ids:
            if not user_id:
                continue
            try:
                user = user_model.objects.get(id=user_id)
            except user_model.DoesNotExist as e:
                logger.warning(e)
                continue

            if user.is_staff or user.is_superuser:
                continue
            if user.is_bailleur():
                # Idée : rajouter le nom du bailleur associé (récupérable dans les habilitations ?)
                result["bailleurs"].append((user.first_name, user.last_name))
            if user.is_instructeur():
                # Idée : rajouter le nom de l'administration (récupérable dans les habilitations ?)
                result["instructeurs"].append((user.first_name, user.last_name))
        result["number"] = len(result["instructeurs"]) + len(result["bailleurs"])
        return result

    def clone_convention(self) -> "Convention":
        """
        Create a shallow clone of this Convention (excluding id and uuid).
        Keeps the same name.
        """
        fields = {
            f.name: getattr(self, f.name)
            for f in self._meta.fields
            if f.name not in ["id", "uuid"]
        }
        return Convention.objects.create(**fields)

    def set_lots(
        self, joined_conventions: list["Convention"], with_remove_joined_convention=True
    ) -> list[Lot] | bool:
        """
        Reassign lots from other conventions to this convention.
        Returns the list of reassigned lots on success, or empty list on failure.
        """
        reassigned_lots = []
        try:
            for convention in joined_conventions:
                for lot in convention.lots.all():
                    if lot is not None:
                        lot.convention = self
                        lot.save()
                        lot.save(update_fields=["convention"])
                        reassigned_lots.append(lot)

                if with_remove_joined_convention:
                    convention.delete()

            return reassigned_lots
        except (ValueError, TypeError) as e:
            logger.error(e)
            return []

    def get_lots(self) -> list[Lot]:
        return self.lots

    def repartition_surfaces(self):
        result = defaultdict(lambda: defaultdict(int))
        data = [lot.repartition_surfaces() for lot in self.lots.all()]
        for entry in data:
            for type_name, subtypes in entry.items():  # INDIVIDUEL / COLLECTIF
                for subtype, value in subtypes.items():  # T1, T2, ..
                    result[type_name][subtype] += value

        # Convert back to normal dicts
        return {t: dict(sub) for t, sub in result.items()}

    def lgts_mixite_sociale_negocies_display(self) -> str:
        return sum(
            [lot.lgts_mixite_sociale_negocies_display() for lot in self.lots.all()]
        )

    def get_lot_with_financement(self, financement):
        return self.lots.filter(
            financement=financement,
        ).first()

    @property
    def logements_import_ordered(self):
        return list(
            chain.from_iterable(
                lot.logements.filter(
                    surface_corrigee__isnull=True, loyer__isnull=False
                ).order_by("import_order")
                for lot in self.lots.all()
            )
        )

    @property
    def logements_sans_loyer_import_ordered(self):
        return list(
            chain.from_iterable(
                lot.logements.filter(
                    surface_corrigee__isnull=True, loyer__isnull=True
                ).order_by("import_order")
                for lot in self.lots.all()
            )
        )

    @property
    def logements_corrigee_import_ordered(self):
        return list(
            chain.from_iterable(
                lot.logements.filter(
                    surface_corrigee__isnull=False, loyer__isnull=False
                ).order_by("import_order")
                for lot in self.lots.all()
            )
        )

    @property
    def logements_corrigee_sans_loyer_import_ordered(self):
        return list(
            chain.from_iterable(
                lot.logements.filter(
                    surface_corrigee__isnull=False, loyer__isnull=True
                ).order_by("import_order")
                for lot in self.lots.all()
            )
        )

    @property
    def annexes(self):
        return chain.from_iterable(lot.annexes.all() for lot in self.lots.all())

    @property
    def stationnements(self):
        return list(
            chain.from_iterable(
                lot.type_stationnements.all() for lot in self.lots.all()
            )
        )

    @property
    def locaux_collectifs(self):
        return list(
            chain.from_iterable(lot.locaux_collectifs.all() for lot in self.lots.all())
        )

    @property
    def prets(self):
        return list(chain.from_iterable(lot.prets.all() for lot in self.lots.all()))
