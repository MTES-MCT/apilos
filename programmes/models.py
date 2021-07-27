import uuid

from django.db import models
from core.models import IngestableModel


class Financement(models.TextChoices):
    PLUS = "PLUS", "PLUS"
    PLAI = "PLAI", "PLAI"
    PLUS_PLAI = "PLUS-PLAI", "PLUS-PLAI"
    PLS = "PLS", "PLS"

class Programme(IngestableModel):
    pivot= ['bailleur', 'nom', 'ville']
    mapping= {
        "nom": 'Nom Opération',
        "code_postal": "Opération code postal",
        "ville": 'Commune',
        "adresse": 'Adresse Opération 1',
        "nb_logements": 'Nb logts',
        "zone_123": 'Zone 123',
        "zone_abc": 'Zone ABC',
        "surface_utile_totale": 'SU totale',
        "annee_gestion_programmation": 'Année Gestion Programmation',
        "numero_gallion": 'N° Opération GALION',
        "type_habitat": "Type d'habitat",
        "bailleur": "MOA (code SIRET)",
        "administration": 'Gestionnaire (code)'
#        "departement": "Département",
    }

    class TypeOperation(models.TextChoices):
        NEUF = "NEUF", "Neuf"
        ACQUIS = "ACQUIS", "Acquis amélioré"
        DEMEMBREMENT = "DEMEMBREMENT", "Démembrement"
        USUFRUIT = "USUFRUIT", "Usufruit"
        VEFA = "VEFA", "VEFA"

    class TypeHabitat(models.TextChoices):
        INDIVIDUEL = "INDIVIDUEL", "Individuel"
        COLLECTIF = "COLLECTIF", "Collectif"

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    administration = models.ForeignKey(
        "instructeurs.Administration", on_delete=models.SET_NULL, null=True
    )
    code_postal = models.CharField(max_length=10, null=True)
    ville = models.CharField(max_length=255, null=True)
    adresse = models.CharField(max_length=255, null=True)
    departement = models.IntegerField(null=True)
    nb_logements = models.IntegerField(null=True)
    numero_gallion = models.CharField(max_length=255, null=True)
    annee_gestion_programmation = models.IntegerField(null=True)
    zone_123 = models.IntegerField(null=True)
    zone_abc = models.CharField(max_length=255, null=True)
    surface_utile_totale = models.FloatField(null=True)
    type_habitat = models.CharField(
        max_length=25,
        choices=TypeHabitat.choices,
        default=TypeHabitat.INDIVIDUEL,
    )
    type_operation = models.CharField(
        max_length=25,
        choices=TypeOperation.choices,
        default=TypeOperation.NEUF,
    )
    anru = models.BooleanField(default=False)
    nb_logement_non_conventionne = models.IntegerField(null=True)
    nb_locaux_commerciaux = models.IntegerField(null=True)
    nb_bureaux = models.IntegerField(null=True)
    vendeur = models.TextField(null=True)
    acquereur = models.TextField(null=True)
    date_acte_notarie = models.DateField(null=True)
    reference_notaire = models.TextField(null=True)
    reference_publication_acte = models.TextField(null=True)
    permis_construire = models.CharField(max_length=255, null=True)
    date_achevement_previsible = models.DateField(null=True)
    date_achat = models.DateField(null=True)
    date_achevement = models.DateField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom


class ReferenceCadastrale(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey("Programme", on_delete=models.CASCADE, null=False)
    section = models.CharField(max_length=255, null=True)
    numero = models.IntegerField(null=True)
    lieudit = models.CharField(max_length=255, null=True)
    surface = models.FloatField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)


class Lot(IngestableModel):
    pivot= ['financement', 'programme']
    mapping= {
        "financement": 'Produit',
        "programme": 'Nom Opération',
        "bailleur": "MOA (code SIRET)",
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    numero = models.IntegerField(null=True)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey("Programme", on_delete=models.CASCADE, null=False)
    financement = models.CharField(
        max_length=25,
        choices=Financement.choices,
        default=Financement.PLUS,
    )
    volumes = models.TextField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)


class Logement(models.Model):
    class TypologieLogement(models.TextChoices):
        T1 = "T1", "T1"
        T2 = "T2", "T2"
        T3 = "T3", "T3"
        T4 = "T4", "T4"
        T5 = "T5", "T5 et plus"

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    designation = models.CharField(max_length=255)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    lot = models.ForeignKey("Lot", on_delete=models.CASCADE, null=False)
    typologie = models.CharField(
        max_length=25,
        choices=TypologieLogement.choices,
        default=TypologieLogement.T1,
    )
    surface_habitable = models.FloatField(null=True)
    surface_annexes = models.FloatField(null=True)
    surface_annexes_retenue = models.FloatField(null=True)
    surface_utile = models.FloatField(null=True)
    loyer_par_metre_carre = models.FloatField(null=True)
    coeficient = models.FloatField(null=True)
    loyer = models.FloatField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)


class Annexe(models.Model):
    class TypologieAnnexe(models.TextChoices):
        BALCON = "BALCON", "Balcon"
        TERRASSE = "TERRASSE", "Terrasse"
        JARDIN = "JARDIN", "Jardin"

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    logement = models.ForeignKey("Logement", on_delete=models.CASCADE, null=False)
    typologie = models.CharField(
        max_length=25,
        choices=TypologieAnnexe.choices,
        default=TypologieAnnexe.BALCON,
    )
    surface_hors_surface_retenue = models.FloatField()
    loyer_par_metre_carre = models.FloatField()
    loyer = models.FloatField()
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)


class TypeStationnement(IngestableModel):
    pivot= ['typologie', 'lot']
    mapping= {
        "typologie": 'Typologie Garage',
        "nb_stationnements": 'Nb Stationnement',
        "loyer": 'Loyer',
        "lot": 'Produit',
        "bailleur": "MOA (code SIRET)",
    }
    class TypologieStationnement(models.TextChoices):
        GARAGE_AERIEN = "GARAGE_AERIEN", "Garage Aérien"
        GARAGE_ENTERRE = "GARAGE_ENTERRE", "Garage enterré"
        PLACE_STATIONNEMENT = "PLACE_STATIONNEMENT", "Place stationnement"

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    lot = models.ForeignKey("Lot", on_delete=models.CASCADE, null=False)
    typologie = models.CharField(
        max_length=25,
        choices=TypologieStationnement.choices,
        default=TypologieStationnement.PLACE_STATIONNEMENT,
    )
    nb_stationnements = models.IntegerField()
    loyer = models.FloatField()
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)
