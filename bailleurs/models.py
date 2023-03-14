import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.models import IngestableModel


class NatureBailleur(models.TextChoices):
    AUTRES = "Autres bailleurs sociaux non HLM", "Autres bailleurs sociaux non HLM"
    PRIVES = "Bailleurs privés", "Bailleurs privés"
    HLM = "HLM", "HLM"
    SEM = "SEM", "SEM"


class SousNatureBailleur(models.TextChoices):
    ASSOCIATIONS = "ASSOCIATIONS", "Associations"
    ANAH = "ANAH", "ANAH"
    COMMERCIALES = "COMMERCIALES", "entreprises commerciales"
    COMMUNE = "COMMUNE", "Commune"
    COOPERATIVE_HLM_SCIC = "COOPERATIVE_HLM_SCIC", "Sté coopérative HLM /SCIC"
    CROUS = "CROUS", "CROUS"
    DEPARTEMENT = "DEPARTEMENT", "Département"
    DRE_DDE_CETE_AC_PREF = "DRE_DDE_CETE_AC_PREF", "DRE,DDE,CETE,AC,Préfect."
    EPCI = "EPCI", "EPCI"
    ETC_PUBLIQUE_LOCAL = "ETC_PUBLIQUE_LOCAL", "Ets public local"
    ETS_HOSTIPATIERS_PRIVES = "ETS_HOSTIPATIERS_PRIVES", "Ets hospitaliers privés"
    FONDATION = "FONDATION", "Fondation"
    FONDATION_HLM = "FONDATION_HLM", "Fondation HLM"
    FRONCIERE_LOGEMENT = "FRONCIERE_LOGEMENT", "Foncière Logement"
    GIP = "GIP", "GIP"
    MUTUELLE = "MUTUELLE", "Mutuelle"
    NONRENSEIGNE = "NONRENSEIGNE", "Non renseigné"
    OFFICE_PUBLIC_HLM = "OFFICE_PUBLIC_HLM", "Office public HLM (OPH)"
    PACT_ARIM = "PACT_ARIM", "Pact-Arim"
    PARTICULIERS = "PARTICULIERS", "Particuliers"
    SA_HLM_ESH = "SA_HLM_ESH", "SA HLM / ESH"
    SACI_CAP = "SACI_CAP", "SACI CAP"
    SEM_EPL = "SEM_EPL", "SEM / EPL"
    UES = "UES", "UES"


NATURE_RELATIONSHIP = {
    SousNatureBailleur.ASSOCIATIONS: NatureBailleur.AUTRES,
    SousNatureBailleur.ANAH: NatureBailleur.AUTRES,
    SousNatureBailleur.COMMERCIALES: NatureBailleur.AUTRES,
    SousNatureBailleur.COMMUNE: NatureBailleur.AUTRES,
    SousNatureBailleur.COOPERATIVE_HLM_SCIC: NatureBailleur.HLM,
    SousNatureBailleur.CROUS: NatureBailleur.AUTRES,
    SousNatureBailleur.DEPARTEMENT: NatureBailleur.AUTRES,
    SousNatureBailleur.DRE_DDE_CETE_AC_PREF: NatureBailleur.AUTRES,
    SousNatureBailleur.EPCI: NatureBailleur.AUTRES,
    SousNatureBailleur.ETC_PUBLIQUE_LOCAL: NatureBailleur.AUTRES,
    SousNatureBailleur.ETS_HOSTIPATIERS_PRIVES: NatureBailleur.AUTRES,
    SousNatureBailleur.FONDATION: NatureBailleur.AUTRES,
    SousNatureBailleur.FONDATION_HLM: NatureBailleur.AUTRES,
    SousNatureBailleur.FRONCIERE_LOGEMENT: NatureBailleur.AUTRES,
    SousNatureBailleur.GIP: NatureBailleur.AUTRES,
    SousNatureBailleur.MUTUELLE: NatureBailleur.AUTRES,
    SousNatureBailleur.OFFICE_PUBLIC_HLM: NatureBailleur.HLM,
    SousNatureBailleur.PACT_ARIM: NatureBailleur.AUTRES,
    SousNatureBailleur.PARTICULIERS: NatureBailleur.PRIVES,
    SousNatureBailleur.SA_HLM_ESH: NatureBailleur.HLM,
    SousNatureBailleur.SACI_CAP: NatureBailleur.AUTRES,
    SousNatureBailleur.SEM_EPL: NatureBailleur.SEM,
    SousNatureBailleur.UES: NatureBailleur.AUTRES,
}


class BailleurManager(models.Manager):
    def get_by_natural_key(self, field, value):
        if field == "siret":
            return self.get(siret=value)

        return self.get(pk=value)


class Bailleur(IngestableModel):
    objects = BailleurManager()

    pivot = "siret"
    mapping = {
        "nom": "MOA (nom officiel)",
        "siret": "MOA (code SIRET)",
        "adresse": "MOA Adresse 1",
        "code_postal": "MOA Code postal",
        "ville": "MOA Ville",
        # "sous_nature_bailleur": "Famille MOA", -> doesn't exists in the last version of file
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bailleurs",
    )
    nom = models.CharField(max_length=255)
    siret = models.CharField(max_length=255, unique=True)
    siren = models.CharField(max_length=255, null=True)
    capital_social = models.FloatField(null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    code_postal = models.CharField(max_length=5, null=True, blank=True)
    ville = models.CharField(max_length=255, null=True, blank=True)
    signataire_nom = models.CharField(max_length=255, null=True, blank=True)
    signataire_fonction = models.CharField(max_length=255, null=True, blank=True)
    signataire_date_deliberation = models.DateField(null=True, blank=True)
    signataire_bloc_signature = models.CharField(max_length=5000, null=True, blank=True)
    operation_exceptionnelle = models.TextField(null=True, blank=True)
    nature_bailleur = models.CharField(
        max_length=255,
        choices=NatureBailleur.choices,
        default=NatureBailleur.AUTRES,
    )
    sous_nature_bailleur = models.CharField(
        max_length=25,
        choices=SousNatureBailleur.choices,
        default=SousNatureBailleur.NONRENSEIGNE,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom}"

    def _get_id(self):
        return self.id

    value = property(_get_id)

    def _get_nom(self):
        return self.nom

    label = property(_get_nom)

    def is_hlm(self):
        return self.nature_bailleur == NatureBailleur.HLM

    def is_sem(self):
        return self.nature_bailleur == NatureBailleur.SEM

    def is_type1and2(self):
        return not self.is_hlm() and not self.is_sem()

    def natural_key(self) -> tuple:
        return tuple(self.siret)


# pylint: disable=W0613
@receiver(pre_save, sender=Bailleur)
def set_bailleur_nature(sender, instance, *args, **kwargs):
    if instance.sous_nature_bailleur in NATURE_RELATIONSHIP:
        instance.nature_bailleur = NATURE_RELATIONSHIP[instance.sous_nature_bailleur]
    if not instance.siren:
        if len(instance.siret) == 14 and instance.siret.isdigit():
            instance.siren = instance.siret[:9]
        else:
            instance.siren = instance.siret
