import uuid

from django.db import models
from programmes.models import Financement
from core import model_utils


class Preteur(models.TextChoices):
    ETAT = "ETAT", "Etat"
    EPCI = "EPCI", "EPCI"
    REGION = "REGION", "Région"
    CDCF = "CDCF", "CDC pour le foncier"
    CDCL = "CDCL", "CDC pour le logement"
    AUTRE = "AUTRE", "Autre"


class ConventionStatut(models.TextChoices):
    # La convention n'est pas ecore soumise à l'instruction
    BROUILLON = "BROUILLON", "Brouillon"
    # La convention est soumise à l'instruction et n'est pas encore validée par l'instructeur
    INSTRUCTION = "INSTRUCTION", "En cours d'instruction"
    # L'instructeur a demandé des corrections au bailleur.
    # Après correction, la convention devra être à nouveau soumise
    CORRECTION = "CORRECTION", "Corrections requises"
    # L'instructeur a validé la convention,
    # le document de convention est édité et il n'a plus qu'à être signé
    VALIDE = "VALIDE", "Validé"
    # La convention est signée et archivée. disponible pour les autres services de l'état
    CLOS = "CLOS", "Convention close"


class Convention(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=255, null=True)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey(
        "programmes.Programme", on_delete=models.CASCADE, null=False
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
        default=ConventionStatut.BROUILLON,
    )
    soumis_le = models.DateTimeField(null=True)
    premiere_soumission_le = models.DateTimeField(null=True)
    valide_le = models.DateTimeField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.programme.ville} - {self.programme.nom} - "
            + f"{self.lot.nb_logements} lgts - {self.lot.financement}"
        )

    # to do:
    # gérer un decorateur :
    # https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#howto-custom-template-tags
    # Ou créé un champ statut
    def is_bailleur_editable(self):
        return (
            self.statut == ConventionStatut.BROUILLON
            or self.statut == ConventionStatut.CORRECTION
        )

    def is_instructeur_editable(self):
        return self.statut != ConventionStatut.CLOS

    def is_submitted(self):
        return self.statut not in [
            ConventionStatut.BROUILLON,
            ConventionStatut.CORRECTION,
        ]

    def comments_text(self):
        return model_utils.get_field_key(self, "comments", "text")

    def comments_files(self):
        return model_utils.get_field_key(self, "comments", "files")

    def get_comments_dict(self):
        result = {}
        for comment in self.comment_set.all():
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

    # Needed to import xlsx files
    import_mapping = {
        "Numéro\n(caractères alphanuméric)": numero,
        "Date d'octroi\n(format dd/mm/yyyy)": date_octroi,
        "Durée\n(en années)": duree,
        "Montant\n(en €)": montant,
        "Prêteur\n(choisir dans la liste déroulante)": preteur,
        "Préciser l'identité du préteur si vous avez sélectionné 'Autre'": autre,
    }
    sheet_name = "Prêts"

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
