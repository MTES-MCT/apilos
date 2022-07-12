import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone
from programmes.models import Financement
from core import model_utils
from users.type_models import TypeRole, EmailPreferences


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

    D/ TRANSMISE : Transmise - Convention transmise
        La convention signée est mise à disposition et automatiquement transmise aux parties et
        partenaires via la plateforme APiLos.
        Anciennement CLOS
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
    TRANSMISE = "5. Transmise", "Convention transmise"
    RESILIEE = "6. Résiliée", "Convention résiliée"


class ConventionType1and2(models.TextChoices):
    TYPE1 = "Type1", "Type I"
    TYPE2 = "Type2", "Type II"


class Convention(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=255, null=True)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey(
        "programmes.Programme",
        related_name="conventions",
        on_delete=models.CASCADE,
        null=False,
    )
    lot = models.ForeignKey("programmes.Lot", on_delete=models.CASCADE, null=False)
    date_fin_conventionnement = models.DateField(null=True)
    financement = models.CharField(
        max_length=25,
        choices=Financement.choices,
        default=Financement.PLUS,
    )
    # fix me: weird to keep fond_propre here
    fond_propre = models.FloatField(null=True)
    comments = models.TextField(null=True)
    statut = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    soumis_le = models.DateTimeField(null=True)
    premiere_soumission_le = models.DateTimeField(null=True)
    valide_le = models.DateTimeField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)
    type1and2 = models.CharField(
        max_length=25, choices=ConventionType1and2.choices, null=True
    )
    type2_lgts_concernes_option1 = models.BooleanField(default=True)
    type2_lgts_concernes_option2 = models.BooleanField(default=True)
    type2_lgts_concernes_option3 = models.BooleanField(default=True)
    type2_lgts_concernes_option4 = models.BooleanField(default=True)
    type2_lgts_concernes_option5 = models.BooleanField(default=True)
    type2_lgts_concernes_option6 = models.BooleanField(default=True)
    type2_lgts_concernes_option7 = models.BooleanField(default=True)
    type2_lgts_concernes_option8 = models.BooleanField(default=True)
    # Missing option for :

    # La présente convention ne prévoyant pas de travaux, le bail entre en vigueur à la date de
    # son acceptation par l'occupant de bonne foi après publication de la convention au fichier
    # immobilier ou son inscription au livre foncier. (7)
    #   OR
    # La présente convention prévoyant des travaux, le bail et, notamment, la clause relative au
    # montant du loyer entre en vigueur à compter de la date d'achèvement des travaux concernant
    # la tranche dans laquelle est compris le logement concerné. (7)

    donnees_validees = models.TextField(null=True)
    fichier_signe = models.CharField(max_length=255, null=True)
    date_resiliation = models.DateField(null=True)

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

    def comments_text(self):
        return model_utils.get_field_key(self, "comments", "text")

    def comments_files(self):
        return model_utils.get_field_key(self, "comments", "files")

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
                self.conventionhistory_set.prefetch_related("user")
                .prefetch_related("user__role_set")
                .filter(
                    statut_convention__in=[
                        ConventionStatut.INSTRUCTION,
                        ConventionStatut.CORRECTION,
                    ],
                    user__role__typologie=role,
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
            return self.conventionhistory_set.filter(
                statut_convention__in=[
                    ConventionStatut.INSTRUCTION,
                    ConventionStatut.CORRECTION,
                ],
            ).latest("cree_le")
        except ConventionHistory.DoesNotExist:
            return None

    def get_email_bailleur_users(self):
        """
        return the email of the bailleurs to send them an email following their email preferences
        partial should include only the bailleur which interact with the convention
        using convention statut
        """
        users_partial = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.conventionhistory_set.filter(
                        user__preferences_email=EmailPreferences.PARTIEL,
                        user__role__typologie=TypeRole.BAILLEUR,
                    ),
                )
            )
        )
        users_all_email = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.bailleur.role_set.filter(
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
        if not self.programme.administration:
            # the programme is not associated to an administration
            # this can occure when the convention is done from scratch
            # should be solved with the association of the commune to DAP (délégataire)
            return []
        if include_partial:
            # All instructeurs of the administration will be notified except one
            # who choose no email (EmailPreferences.AUCUN)
            return list(
                set(
                    map(
                        lambda x: x.user.email,
                        self.programme.administration.role_set.filter(
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
                    self.conventionhistory_set.filter(
                        user__preferences_email=EmailPreferences.PARTIEL,
                        user__role__typologie=TypeRole.INSTRUCTEUR,
                    ),
                )
            )
        )
        users_all_email = list(
            set(
                map(
                    lambda x: x.user.email,
                    self.programme.administration.role_set.filter(
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
                .replace("{zone}", str(self.programme.zone_123_bis))
                .replace("{mois}", str(timezone.now().month))
                .replace("{année}", str(timezone.now().year))
            )
        return None

    def is_project(self):
        return self.statut == ConventionStatut.PROJET

    def display_options(self):
        return {
            "display_comments": self.statut
            in [
                ConventionStatut.INSTRUCTION,
                ConventionStatut.CORRECTION,
                ConventionStatut.A_SIGNER,
                ConventionStatut.TRANSMISE,
            ],
            "display_comments_summary": self.statut
            in [
                ConventionStatut.INSTRUCTION,
                ConventionStatut.CORRECTION,
            ],
            "display_validation": self.statut
            in [
                ConventionStatut.INSTRUCTION,
                ConventionStatut.CORRECTION,
            ],
            "display_is_validated": self.statut
            in [
                ConventionStatut.A_SIGNER,
                ConventionStatut.TRANSMISE,
                ConventionStatut.RESILIEE,
            ],
            "display_notification": self.statut
            in [
                ConventionStatut.INSTRUCTION,
                ConventionStatut.CORRECTION,
            ],
            "display_demande_correction": self.statut
            in [
                ConventionStatut.INSTRUCTION,
            ],
            "display_demande_instruction": self.statut
            in [
                ConventionStatut.CORRECTION,
            ],
            "display_redirect_sent": self.statut
            in [
                ConventionStatut.A_SIGNER,
                ConventionStatut.TRANSMISE,
            ],
            "display_progress_bar_1": self.statut
            in [
                ConventionStatut.PROJET,
                ConventionStatut.INSTRUCTION,
                ConventionStatut.CORRECTION,
            ],
            "display_progress_bar_2": self.statut
            in [
                ConventionStatut.A_SIGNER,
            ],
            "display_progress_bar_3": self.statut
            in [
                ConventionStatut.TRANSMISE,
            ],
            "display_type1and2_editable": self.statut
            in [
                ConventionStatut.PROJET,
                ConventionStatut.INSTRUCTION,
                ConventionStatut.CORRECTION,
            ],
            "display_back_to_instruction": self.statut
            in [
                ConventionStatut.A_SIGNER,
            ],
        }

    def statut_for_template(self):
        return {
            "statut": self.statut,
            "statut_display": self.get_statut_display(),
            "short_statut": (
                "Projet (Brouillon)"
                if self.statut == ConventionStatut.PROJET
                else self.statut[3:]
            ),
            "key_statut": self.statut[3:].replace(" ", "_").replace("é", "e"),
        }

    def mixity_option(self):
        """
        return True if the option regarding the number of lodging in addition to loan to people
        with low revenu should be displayed in the interface and fill in the convention document
        Should be editable when it is a PLUS convention
        """
        return self.financement == Financement.PLUS

    def type1and2_configuration_not_needed(self):
        return not (self.bailleur.is_type1and2() and not self.type1and2)

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


class ConventionHistory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    convention = models.ForeignKey("Convention", on_delete=models.CASCADE, null=False)
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
    commentaire = models.TextField(null=True)
    user = models.ForeignKey(
        "users.User", related_name="valide_par", on_delete=models.SET_NULL, null=True
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)


class Pret(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    convention = models.ForeignKey("Convention", on_delete=models.CASCADE, null=False)
    preteur = models.CharField(
        max_length=25,
        choices=Preteur.choices,
        default=Preteur.AUTRE,
    )
    autre = models.CharField(null=True, max_length=255)
    date_octroi = models.DateField(null=True)
    numero = models.CharField(null=True, max_length=255)
    duree = models.IntegerField(null=True)
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
