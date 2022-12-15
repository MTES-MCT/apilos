import uuid

from django.db import models
from django.db.models import Q
from django.forms import model_to_dict
from django.utils import timezone

from ecoloweb.models import EcoloReference
from programmes.models import (
    Annexe,
    Financement,
    Logement,
    Lot,
    Programme,
    TypeStationnement,
)
from users.type_models import EmailPreferences, TypeRole


class Preteur(models.TextChoices):
    ETAT = "ETAT", "Etat"
    EPCI = "EPCI", "EPCI"
    REGION = "REGION", "Région"
    VILLE = "VILLE", "Ville"
    CDCF = "CDCF", "CDC pour le foncier"
    CDCL = "CDCL", "CDC pour le logement"
    COMMUNE = "COMMUNE", "Commune et action logement"
    ANRU = "ANRU", "ANRU"
    AUTRE = "AUTRE", "Autre"


class ConventionStatut(models.TextChoices):
    """
    A/ PROJET : Projet - Création d'un projet de convention
        Le bailleur crée un projet de convention APL, il ajoute à ce projet des documents
        et des informations concernant les logements de l'opération.
        Anciennement BROUILLON

    B/ Instruction (2 sous-statuts) : Instruction du projet de convention
        Le bailleur et l'instructeur échangent et s'alignent sur le contenu de la convention

        B1/ INSTRUCTION : Instruction requise - Projet de convention soumis à l'instruction
            L'instructeur vérifie le contenu du projet de convention et, si nécessaire,
            transmet au bailleur ses demandes de modifications
            Anciennement INSTRUCTION

        B2/ CORRECTION : Corrections requises - Projet de convention à modifier par le bailleur
            Le bailleur intègre les demandes de modification et soumet à nouveau le projet de
            convention à l'instructeur
            Anciennement CORRECTION

    C/ A_SIGNER : A signer - Convention à signer
        Le bailleur et l'instructeur sont d'accord sur le projet de convention. Les parties
        procèdent à la signature.
        Anciennement VALIDE

    D/ SIGNEE : Signée - Convention signée
        La convention signée est mise à disposition via la plateforme APiLos.
        Anciennement CLOS

    E/ RESILIEE: Résilié - Convention résiliée

    F/ DENONCEE: Dénoncée - Convention dénoncée
        Le bailleur décide, une fois la période de couverture de la convention achevée, de
        dénoncer la convention et rendre ainsi caduques toutes les clauses d'encadrement qui
        y étaient définies. Il est seul décideur, cependant depuis peu une commune considérée
        comme en "carence" de logement social peut s'opposer à cette dénonciation.

    G/ ANNULEE: Annulée en suivi - Convention annulée
        Les 2 parties s'entendent pour annuler la convention

    """

    PROJET = "1. Projet", "Création d'un projet de convention"
    INSTRUCTION = (
        "2. Instruction requise",
        "Projet de convention soumis à l'instruction",
    )
    CORRECTION = (
        "3. Corrections requises",
        "Projet de convention à modifier par le bailleur",
    )
    A_SIGNER = "4. A signer", "Convention à signer"
    SIGNEE = "5. Signée", "Convention signée"
    RESILIEE = "6. Résiliée", "Convention résiliée"
    DENONCEE = "7. Dénoncée", "Convention dénoncée"
    ANNULEE = "8. Annulée en suivi", "Convention annulée en suivi"


class AvenantType(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255, unique=True)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom}"

    @classmethod
    def get_as_choices(cls):
        return [
            (avenant_type.nom, avenant_type.nom) for avenant_type in cls.objects.all()
        ]


class ConventionType1and2(models.TextChoices):
    TYPE1 = "Type1", "Type I"
    TYPE2 = "Type2", "Type II"


class Convention(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="avenants",
    )
    numero = models.CharField(max_length=255, null=True, blank=True)
    programme = models.ForeignKey(
        "programmes.Programme",
        related_name="conventions",
        on_delete=models.CASCADE,
        null=False,
    )
    lot = models.ForeignKey(
        "programmes.Lot",
        on_delete=models.CASCADE,
        null=False,
        related_name="conventions",
    )
    date_fin_conventionnement = models.DateField(null=True, blank=True)
    financement = models.CharField(
        max_length=25,
        choices=Financement.choices,
        default=Financement.PLUS,
    )
    # fix me: weird to keep fond_propre here
    fond_propre = models.FloatField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    statut = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    soumis_le = models.DateTimeField(null=True, blank=True)
    premiere_soumission_le = models.DateTimeField(null=True, blank=True)
    valide_le = models.DateTimeField(null=True, blank=True)
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
        related_name="avenant_types",
        verbose_name="Type d'avenant",
    )
    signataire_nom = models.CharField(max_length=255, null=True)
    signataire_fonction = models.CharField(max_length=255, null=True)
    signataire_date_deliberation = models.DateField(null=True)
    # Champs liés au SPF (Service de Publication Foncière))
    date_publication_spf = models.DateField(null=True)
    reference_spf = models.CharField(max_length=50, null=True)
    date_envoi_spf = models.DateField(null=True)
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

    donnees_validees = models.TextField(null=True, blank=True)
    nom_fichier_signe = models.CharField(max_length=255, null=True, blank=True)
    televersement_convention_signee_le = models.DateTimeField(null=True, blank=True)
    date_resiliation = models.DateField(null=True, blank=True)

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
        null=True, blank=True, max_length=5000
    )
    attribution_inclusif_conditions_admission = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_inclusif_modalites_attribution = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_inclusif_partenariats = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_inclusif_activites = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_reservation_prefectoral = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_modalites_reservations = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_modalites_choix_personnes = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_prestations_integrees = models.CharField(
        null=True, blank=True, max_length=5000
    )
    attribution_prestations_facultatives = models.CharField(
        null=True, blank=True, max_length=5000
    )

    # Needed for admin
    @property
    def administration(self):
        return self.programme.administration

    @property
    def bailleur(self):
        return self.programme.bailleur

    @property
    def ecolo_reference(self) -> EcoloReference | None:
        if self.id is not None:
            return EcoloReference.objects.filter(
                apilos_model="conventions.Convention", apilos_id=self.id
            ).first()

        return None

    @property
    def bailleur_id(self):
        return self.programme.bailleur_id

    def __str__(self):
        programme = self.programme
        lot = self.lot
        return (
            f"{programme.ville} - {programme.nom} - "
            + f"{lot.nb_logements} lgts - {lot.get_type_habitat_display()} - {lot.financement}"
        )

    def is_bailleur_editable(self):
        return self.statut in (
            ConventionStatut.PROJET,
            ConventionStatut.CORRECTION,
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

    def get_last_notification_by_role(self, role: TypeRole):
        try:
            return (
                self.conventionhistories.prefetch_related("user")
                .prefetch_related("user__roles")
                .filter(
                    statut_convention__in=[
                        ConventionStatut.INSTRUCTION,
                        ConventionStatut.CORRECTION,
                    ],
                    user__roles__typologie=role,
                )
                .latest("cree_le")
            )
        except ConventionHistory.DoesNotExist:
            return None

    def get_last_bailleur_notification(self):
        return self.get_last_notification_by_role(TypeRole.BAILLEUR)

    def get_last_instructeur_notification(self):
        return self.get_last_notification_by_role(TypeRole.INSTRUCTEUR)

    def get_last_submission(self):
        try:
            return self.conventionhistories.filter(
                statut_convention__in=[
                    ConventionStatut.INSTRUCTION,
                    ConventionStatut.CORRECTION,
                ],
            ).latest("cree_le")
        except ConventionHistory.DoesNotExist:
            return None

    def get_email_bailleur_users(self, all_bailleur_users=False):
        """
        return the email of the bailleurs to send them an email following their email preferences
        partial should include only the bailleur which interact with the convention
        using convention statut
        """
        if all_bailleur_users:
            return list(
                set(
                    map(
                        lambda x: x.email,
                        [
                            r.user
                            for r in self.programme.bailleur.roles.all()
                            if r.user.preferences_email != EmailPreferences.AUCUN
                        ],
                    )
                )
            )
        users_partial = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.conventionhistories.filter(
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
                    self.programme.bailleur.roles.filter(
                        user__preferences_email=EmailPreferences.TOUS
                    ),
                )
            )
        )
        return users_partial + users_all_email

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
                        self.programme.administration.roles.filter(
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
                    self.conventionhistories.filter(
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
                    self.programme.administration.roles.filter(
                        user__preferences_email=EmailPreferences.TOUS
                    ),
                )
            )
        )
        return users_partial + users_all_email

    def get_convention_prefix(self):
        if self.programme.administration:
            return (
                self.programme.administration.prefix_convention.replace(
                    "{département}",
                    self.programme.code_postal[:-3]
                    if self.programme.code_postal
                    else "",
                )
                .replace("{zone}", str(self.programme.zone_123))
                .replace("{mois}", str(timezone.now().month))
                .replace("{année}", str(timezone.now().year))
            )
        return None

    def is_avenant(self):
        return self.parent_id is not None

    def statut_for_template(self):
        return {
            "statut": self.statut,
            "statut_display": self.get_statut_display(),
            "key_statut": self.statut[3:].replace(" ", "_").replace("é", "e"),
        }

    def short_statut_for_template(self):
        short_status = {
            ConventionStatut.PROJET: "Projet",
            ConventionStatut.INSTRUCTION: "A instruire",
            ConventionStatut.CORRECTION: "En attente de corrections",
            ConventionStatut.A_SIGNER: "En attente de signature",
            ConventionStatut.SIGNEE: "Finalisée",
            ConventionStatut.RESILIEE: "Résiliée",
        }
        return f"{short_status.get(self.statut)}"

    def mixity_option(self):
        """
        return True if the option regarding the number of lodging in addition to loan to people
        with low revenu should be displayed in the interface and fill in the convention document
        Should be editable when it is a PLUS convention
        """
        return self.financement == Financement.PLUS

    def display_not_validated_status(self):
        """
        Text display as Watermark when the convention is in project or instruction status
        """
        if self.statut == ConventionStatut.PROJET:
            return "Projet de convention"
        if self.statut in [
            ConventionStatut.INSTRUCTION,
            ConventionStatut.CORRECTION,
        ]:
            return "Convention en cours d'instruction"
        return ""

    def clone(self, user, *, convention_origin):
        # pylint: disable=R0914
        programme_fields = model_to_dict(
            self.programme,
            exclude=[
                "id",
                "parent",
                "parent_id",
                "cree_le",
                "mis_a_jour_le",
            ],
        )
        programme_fields.update(
            {
                "bailleur_id": programme_fields.pop("bailleur"),
                "administration_id": programme_fields.pop("administration"),
                "parent_id": convention_origin.programme_id,
            }
        )
        cloned_programme = Programme.objects.create(**programme_fields)
        cloned_programme.save()

        lot_fields = model_to_dict(
            self.lot,
            exclude=[
                "id",
                "parent",
                "parent_id",
                "programme",
                "programme_id",
                "cree_le",
                "mis_a_jour_le",
            ],
        )
        lot_fields.update(
            {
                "programme": cloned_programme,
                "parent_id": convention_origin.lot_id,
            }
        )
        cloned_lot = Lot(**lot_fields)
        cloned_lot.save()

        convention_fields = model_to_dict(
            self,
            exclude=[
                "avenant_types",
                "comments",
                "cree_le",
                "date_resiliation",
                "donnees_validees",
                "id",
                "lot_id",
                "lot",
                "mis_a_jour_le",
                "nom_fichier_signe",
                "numero",
                "parent_id",
                "parent",
                "premiere_soumission_le",
                "programme_id",
                "programme",
                "soumis_le",
                "televersement_convention_signee_le",
                "valide_le",
            ],
        )
        convention_fields.update(
            {
                "programme": cloned_programme,
                "lot": cloned_lot,
                "parent_id": convention_origin.id,
                "statut": ConventionStatut.PROJET,
                "cree_par": user,
            }
        )
        cloned_convention = Convention(**convention_fields)
        cloned_convention.save()

        for logement in self.lot.logements.all():
            logement_fields = model_to_dict(
                logement,
                exclude=[
                    "id",
                    "lot",
                    "cree_le",
                    "mis_a_jour_le",
                ],
            )
            logement_fields.update(
                {
                    "lot": cloned_lot,
                }
            )
            cloned_logement = Logement(**logement_fields)
            cloned_logement.save()
            for annexe in logement.annexes.all():
                annexe_fields = model_to_dict(
                    annexe,
                    exclude=[
                        "id",
                        "logement",
                        "cree_le",
                        "mis_a_jour_le",
                    ],
                )
                annexe_fields.update(
                    {
                        "logement": cloned_logement,
                    }
                )
                cloned_annexe = Annexe(**annexe_fields)
                cloned_annexe.save()

        for type_stationnement in self.lot.type_stationnements.all():
            type_stationnement_fields = model_to_dict(
                type_stationnement,
                exclude=[
                    "id",
                    "lot",
                    "cree_le",
                    "mis_a_jour_le",
                ],
            )
            type_stationnement_fields.update(
                {
                    "lot": cloned_lot,
                }
            )
            cloned_type_stationnement = TypeStationnement(**type_stationnement_fields)
            cloned_type_stationnement.save()
        return cloned_convention

    def get_default_convention_number(self):
        if self.is_avenant():
            parent = self.parent
            nb_validated_avenants = parent.avenants.exclude(
                statut__in=[
                    ConventionStatut.PROJET,
                    ConventionStatut.INSTRUCTION,
                    ConventionStatut.CORRECTION,
                ]
            ).count()
            return str(nb_validated_avenants + 1)
        return (
            self.numero
            if self.numero
            else self.get_convention_prefix()
            if self.programme.administration
            else ""
        )


class ConventionHistory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention",
        on_delete=models.CASCADE,
        null=False,
        related_name="conventionhistories",
    )
    statut_convention = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    statut_convention_precedent = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    commentaire = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        "users.User",
        related_name="valide_par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    # Needed for admin
    @property
    def bailleur(self):
        return self.convention.programme.bailleur


class Pret(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention", on_delete=models.CASCADE, null=False, related_name="prets"
    )
    preteur = models.CharField(
        max_length=25,
        choices=Preteur.choices,
        default=Preteur.AUTRE,
    )
    autre = models.CharField(null=True, blank=True, max_length=255)
    date_octroi = models.DateField(null=True, blank=True)
    numero = models.CharField(null=True, blank=True, max_length=255)
    duree = models.IntegerField(null=True, blank=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    # Needed to import xlsx files
    import_mapping = {
        "Numéro\n(caractères alphanuméric)": numero,
        "Date d'octroi\n(format dd/mm/yyyy)": date_octroi,
        "Durée\n(en années)": duree,
        "Montant\n(en €)": montant,
        "Prêteur\n(choisir dans la liste déroulante)": preteur,
        "Préciser l'identité du préteur si vous avez sélectionné 'Autre'": autre,
    }
    sheet_name = "Financements"

    # Needed for admin
    @property
    def bailleur(self):
        return self.convention.programme.bailleur

    def _get_preteur(self):
        return self.get_preteur_display()

    p = property(_get_preteur)

    def _get_autre(self):
        return self.autre

    a = property(_get_autre)

    def _get_date_octroi(self):
        return self.date_octroi

    do = property(_get_date_octroi)

    def _get_numero(self):
        return self.numero

    n = property(_get_numero)

    def _get_duree(self):
        return self.duree

    d = property(_get_duree)

    def _get_montant(self):
        return self.montant

    m = property(_get_montant)

    def p_full(self):
        return self.get_preteur_display().replace(
            "CDC", "Caisse de Dépôts et Consignation"
        )

    def preteur_display(self):
        if self.preteur == Preteur.AUTRE:
            return self.autre
        return self.p_full()


class PieceJointeType(models.TextChoices):
    CONVENTION = "CONVENTION", "Convention APL"
    RECTIFICATION = (
        "RECTIFICATION",
        "Demande de rectification(s) du bureau des hypothèques",
    )
    ATTESTATION_PREFECTORALE = "ATTESTATION_PREFECTORALE", "Attestations préfectorales"
    AVENANT = "AVENANT", "Avenant"
    PHOTO = "PHOTO", "Photographie du bâti ou des logements"
    AUTRE = "AUTRE", "Autre"


class PieceJointe(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention",
        on_delete=models.CASCADE,
        null=False,
        related_name="pieces_jointes",
    )
    type = models.CharField(
        null=True,
        max_length=24,
        choices=PieceJointeType.choices,
        default=PieceJointeType.AUTRE,
    )
    fichier = models.CharField(null=True, blank=True, max_length=255)
    nom_reel = models.CharField(null=True, blank=True, max_length=255)
    description = models.CharField(null=True, blank=True, max_length=255)
    cree_le = models.DateTimeField(auto_now_add=False)

    def is_convention(self) -> bool:
        return self.type == PieceJointeType.CONVENTION
