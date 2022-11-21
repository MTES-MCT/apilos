import uuid

from django.db import models

from core.models import IngestableModel


class SousNatureBailleur(models.TextChoices):
    ASSOCIATIONS = "ASSOCIATIONS", "Associations"
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


class Bailleur(IngestableModel):
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
    siret = models.CharField(max_length=14, unique=True)
    siren = models.CharField(max_length=9, null=True)
    capital_social = models.FloatField(null=True)
    adresse = models.CharField(max_length=255, null=True)
    code_postal = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    signataire_nom = models.CharField(max_length=255, null=True)
    signataire_fonction = models.CharField(max_length=255, null=True)
    signataire_date_deliberation = models.DateField(null=True)
    operation_exceptionnelle = models.TextField(null=True)
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
        return self.sous_nature_bailleur in [
            SousNatureBailleur.OFFICE_PUBLIC_HLM,
            SousNatureBailleur.SA_HLM_ESH,
            SousNatureBailleur.COOPERATIVE_HLM_SCIC,
        ]

    def is_sem(self):
        return self.sous_nature_bailleur in [SousNatureBailleur.SEM_EPL]

    def is_type1and2(self):
        return not self.is_hlm() and not self.is_sem()
