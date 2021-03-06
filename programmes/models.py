import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.models import IngestableModel
from core import model_utils


class Zone123(models.TextChoices):
    Zone1 = "1", "01"
    Zone2 = "2", "02"
    Zone3 = "3", "03"
    Zone1bis = "1bis", "1bis"


class ZoneABC(models.TextChoices):
    ZoneA = "A", "A"
    ZoneAbis = "Abis", "Abis"
    ZoneB1 = "B1", "B1"
    ZoneB2 = "B2", "B2"
    ZoneC = "C", "C"


class Financement(models.TextChoices):
    PLUS = "PLUS", "PLUS"
    PLAI = "PLAI", "PLAI"
    PLAI_ADP = "PLAI_ADP", "PLAI_ADP"
    PLUS_PLAI = "PLUS-PLAI", "PLUS-PLAI"
    PLS = "PLS", "PLS"
    PSH = "PSH", "PSH"
    PALULOS = "PALULOS", "PALULOS"
    SANS_FINANCEMENT = "SANS_FINANCEMENT", "Sans Financement"


class FinancementEDD(models.TextChoices):
    PLUS = "PLUS", "PLUS"
    PLAI = "PLAI", "PLAI"
    PLAI_ADP = "PLAI_ADP", "PLAI_ADP"
    PLS = "PLS", "PLS"
    SANS_FINANCEMENT = "SANS_FINANCEMENT", "Sans Financement"


class TypologieLogement(models.TextChoices):
    T1 = "T1", "T1"
    T2 = "T2", "T2"
    T3 = "T3", "T3"
    T4 = "T4", "T4"
    T5 = "T5", "T5 et plus"

    @classmethod
    def map_string(cls, value):
        mapping = {
            "1": "T1",
            "2": "T2",
            "3": "T3",
            "4": "T4",
            "5": "T5 et plus",
            "5 et plus": "T5 et plus",
            "6": "T5 et plus",
            "7": "T5 et plus",
            "8": "T5 et plus",
            "9": "T5 et plus",
            "10": "T5 et plus",
        }
        value = str(value)
        if value in mapping:
            return mapping[value]
        return value


class NatureLogement(models.TextChoices):
    SANSOBJET = "SANSOBJET", "Sans Objet"
    LOGEMENTSORDINAIRES = "LOGEMENTSORDINAIRES", "Logements ordinaires"
    AUTRE = "AUTRE", "Autres logements foyers"
    HEBERGEMENT = "HEBERGEMENT", "Hébergement"
    RESISDENCESOCIALE = "RESISDENCESOCIALE", "Résidence sociale"
    PENSIONSDEFAMILLE = "PENSIONSDEFAMILLE", "Pensions de famille (Maisons relais)"
    RESIDENCEDACCUEIL = "RESIDENCEDACCUEIL", "Résidence d'accueil"
    RESIDENCEUNIVERSITAIRE = "RESIDENCEUNIVERSITAIRE", "Résidence universitaire"
    RHVS = "RHVS", "RHVS"


class TypeOperation(models.TextChoices):
    SANSOBJET = "SANSOBJET", "Sans Objet"
    NEUF = "NEUF", "Construction Neuve"
    VEFA = "VEFA", "Construction Neuve > VEFA"
    ACQUIS = "ACQUIS", "Acquisition"
    ACQUISAMELIORATION = "ACQUISAMELIORATION", "Acquisition-Amélioration"
    REHABILITATION = "REHABILITATION", "Réhabilitation"
    ACQUISSANSTRAVAUX = "ACQUISSANSTRAVAUX", "Acquisition sans travaux"
    SANSTRAVAUX = "SANSTRAVAUX", "Sans aide financière (sans travaux)"
    USUFRUIT = "USUFRUIT", "Usufruit"


class TypeHabitat(models.TextChoices):
    MIXTE = "MIXTE", "Mixte"
    INDIVIDUEL = "INDIVIDUEL", "Individuel"
    COLLECTIF = "COLLECTIF", "Collectif"


class TypologieAnnexe(models.TextChoices):
    TERRASSE = "TERRASSE", "Terrasse"
    JARDIN = "JARDIN", "Jardin"
    CAVE = "CAVE", "Cave"


class TypologieStationnement(models.TextChoices):
    GARAGE_AERIEN = "GARAGE_AERIEN", "Garage aérien"
    GARAGE_ENTERRE = "GARAGE_ENTERRE", "Garage enterré"
    PLACE_STATIONNEMENT = "PLACE_STATIONNEMENT", "Place de stationnement"
    PARKING_EXTERIEUR_PRIVATIF = (
        "PARKING_EXTERIEUR_PRIVATIF",
        "Parking extérieur privatif",
    )
    PARKING_SOUSSOL = "PARKING_SOUSSOL", "Parking en sous-sol ou en superstructure"
    GARAGE_BOXE_SIMPLE = "GARAGE_BOXE_SIMPLE", "Garage boxé simple"
    GARAGE_BOXE_DOUBLE = "GARAGE_BOXE_DOUBLE", "Garage boxé double"
    EXTERIEUR_BOXE = "EXTERIEUR_BOXE", "extérieur boxé"
    SOUSSOL_BOXE = "SOUSSOL_BOXE", "en sous-sol boxé"
    CARPORT = "CARPORT", "Carport"
    DEUX_ROUES_EXTERIEUR = "DEUX_ROUES_EXTERIEUR", "2 roues en extérieur"
    DEUX_ROUES_SOUSSOL = "DEUX_ROUES_SOUSSOL", "2 roues en sous-sol"
    DOUBLE_SOUSSOL = "DOUBLE_SOUSSOL", "Parking double en sous-sol"
    DOUBLE_SUPERSTRUCTURE = "DOUBLE_SUPERSTRUCTURE", "Parking double en superstructure"


class Programme(IngestableModel):
    pivot = ["bailleur", "nom", "ville"]
    mapping = {
        "nom": "Nom Opération",
        "code_postal": "Opération code postal",
        "ville": "Commune",
        "adresse": "Adresse Opération 1",
        "zone_123": "Zone 123",
        "zone_abc": "Zone ABC",
        "surface_utile_totale": "SU totale",
        "annee_gestion_programmation": "Année Programmation retenue",
        "numero_galion": "N° Opération GALION",
        "bailleur": "MOA (code SIRET)",
        "administration": "Gestionnaire (code)",
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    numero_galion = models.CharField(max_length=255, null=True)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    administration = models.ForeignKey(
        "instructeurs.Administration", on_delete=models.SET_NULL, null=True
    )
    adresse = models.TextField(null=True)
    code_postal = models.CharField(max_length=10, null=True)
    ville = models.CharField(max_length=255, null=True)
    code_insee_commune = models.CharField(max_length=10, null=True)
    code_insee_departement = models.CharField(max_length=10, null=True)
    code_insee_region = models.CharField(max_length=10, null=True)
    annee_gestion_programmation = models.IntegerField(null=True)

    zone_123 = models.CharField(
        max_length=25,
        choices=Zone123.choices,
        default=None,
        null=True,
    )
    zone_abc = models.CharField(
        max_length=25,
        choices=ZoneABC.choices,
        default=None,
        null=True,
    )

    surface_utile_totale = models.DecimalField(
        max_digits=8, decimal_places=2, null=True
    )
    type_operation = models.CharField(
        max_length=25,
        choices=TypeOperation.choices,
        default=TypeOperation.NEUF,
    )
    nature_logement = models.CharField(
        max_length=25,
        choices=NatureLogement.choices,
        default=NatureLogement.LOGEMENTSORDINAIRES,
    )
    anru = models.BooleanField(default=False)
    nb_locaux_commerciaux = models.IntegerField(null=True)
    nb_bureaux = models.IntegerField(null=True)
    autres_locaux_hors_convention = models.TextField(null=True)
    vendeur = models.TextField(null=True)
    acquereur = models.TextField(null=True)
    date_acte_notarie = models.DateField(null=True)
    reference_notaire = models.TextField(null=True)
    reference_publication_acte = models.TextField(null=True)
    acte_de_propriete = models.TextField(null=True)
    effet_relatif = models.TextField(null=True)
    certificat_adressage = models.TextField(null=True)
    reference_cadastrale = models.TextField(null=True)
    edd_volumetrique = models.TextField(max_length=5000, null=True)
    mention_publication_edd_volumetrique = models.TextField(max_length=1000, null=True)
    edd_classique = models.TextField(max_length=5000, null=True)
    mention_publication_edd_classique = models.TextField(max_length=1000, null=True)
    permis_construire = models.CharField(max_length=255, null=True)
    date_achevement_previsible = models.DateField(null=True)
    date_achat = models.DateField(null=True)
    date_achevement = models.DateField(null=True)
    date_achevement_compile = models.DateField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    def get_type_operation_advanced_display(self):
        prefix = "en "
        if self.type_operation == TypeOperation.SANSTRAVAUX:
            prefix = ""
        return (
            " " + prefix + self.get_type_operation_display().lower()
            if self.type_operation != TypeOperation.SANSOBJET
            else ""
        )

    def vendeur_text(self):
        return model_utils.get_field_key(self, "vendeur", "text")

    def vendeur_files(self):
        return model_utils.get_field_key(self, "vendeur", "files", default={})

    def acquereur_text(self):
        return model_utils.get_field_key(self, "acquereur", "text")

    def acquereur_files(self):
        return model_utils.get_field_key(self, "acquereur", "files", default={})

    def reference_notaire_text(self):
        return model_utils.get_field_key(self, "reference_notaire", "text")

    def reference_notaire_files(self):
        return model_utils.get_field_key(self, "reference_notaire", "files", default={})

    def reference_publication_acte_text(self):
        return model_utils.get_field_key(self, "reference_publication_acte", "text")

    def reference_publication_acte_files(self):
        return model_utils.get_field_key(
            self, "reference_publication_acte", "files", default={}
        )

    def acte_de_propriete_files(self):
        return model_utils.get_field_key(self, "acte_de_propriete", "files", default={})

    def certificat_adressage_files(self):
        return model_utils.get_field_key(
            self, "certificat_adressage", "files", default={}
        )

    def effet_relatif_files(self):
        return model_utils.get_field_key(self, "effet_relatif", "files", default={})

    def reference_cadastrale_files(self):
        return model_utils.get_field_key(
            self, "reference_cadastrale", "files", default={}
        )

    def edd_volumetrique_text(self):
        return model_utils.get_field_key(self, "edd_volumetrique", "text")

    def edd_volumetrique_files(self):
        return model_utils.get_field_key(self, "edd_volumetrique", "files", default={})

    def edd_classique_text(self):
        return model_utils.get_field_key(self, "edd_classique", "text")

    def edd_classique_files(self):
        return model_utils.get_field_key(self, "edd_classique", "files", default={})


# pylint: disable=W0613
@receiver(pre_save, sender=Programme)
def compute_date_achevement_compile(sender, instance, *args, **kwargs):
    instance.date_achevement_compile = (
        instance.date_achevement or instance.date_achevement_previsible
    )


class LogementEDD(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    designation = models.CharField(max_length=255)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey("Programme", on_delete=models.CASCADE, null=False)
    financement = models.CharField(
        max_length=25,
        choices=FinancementEDD.choices,
        default=FinancementEDD.PLUS,
    )
    numero_lot = models.CharField(max_length=255, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)
    lot_num = 0

    import_mapping = {
        "Désignation des logements": designation,
        "Financement": financement,
        "Numéro de lot des logements": numero_lot,
    }
    sheet_name = "EDD Simplifié"

    def __str__(self):
        return self.designation


class ReferenceCadastrale(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey("Programme", on_delete=models.CASCADE, null=False)
    section = models.CharField(max_length=255, null=True)
    numero = models.IntegerField(null=True)
    lieudit = models.CharField(max_length=255, null=True)
    surface = models.CharField(max_length=255, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    import_mapping = {
        "Section": section,
        "Numéro": numero,
        "Lieudit": lieudit,
        "Surface": surface,
    }
    sheet_name = "Références Cadastrales"

    def __str__(self):
        return f"{self.section} - {self.numero} - {self.lieudit}"


class Lot(IngestableModel):
    pivot = ["financement", "programme", "type_habitat"]
    mapping = {
        "financement": "Produit",
        "programme": "Nom Opération",
        "bailleur": "MOA (code SIRET)",
        "nb_logements": "Nb logts",
        "type_habitat": "Type d'habitat",
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nb_logements = models.IntegerField(null=True)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    programme = models.ForeignKey("Programme", on_delete=models.CASCADE, null=False)
    financement = models.CharField(
        max_length=25,
        choices=Financement.choices,
        default=Financement.PLUS,
    )
    type_habitat = models.CharField(
        max_length=25,
        choices=TypeHabitat.choices,
        default=TypeHabitat.INDIVIDUEL,
    )
    edd_volumetrique = models.TextField(max_length=50000, null=True)
    edd_classique = models.TextField(max_length=50000, null=True)
    annexe_caves = models.BooleanField(default=False)
    annexe_soussols = models.BooleanField(default=False)
    annexe_remises = models.BooleanField(default=False)
    annexe_ateliers = models.BooleanField(default=False)
    annexe_sechoirs = models.BooleanField(default=False)
    annexe_celliers = models.BooleanField(default=False)
    annexe_resserres = models.BooleanField(default=False)
    annexe_combles = models.BooleanField(default=False)
    annexe_balcons = models.BooleanField(default=False)
    annexe_loggias = models.BooleanField(default=False)
    annexe_terrasses = models.BooleanField(default=False)
    lgts_mixite_sociale_negocies = models.IntegerField(default=0)
    loyer_derogatoire = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        verbose_name="Loyer dérogatoire",
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def edd_volumetrique_text(self):
        return model_utils.get_field_key(self, "edd_volumetrique", "text")

    def edd_volumetrique_files(self):
        return model_utils.get_field_key(self, "edd_volumetrique", "files", default={})

    def edd_classique_text(self):
        return model_utils.get_field_key(self, "edd_classique", "text")

    def edd_classique_files(self):
        return model_utils.get_field_key(self, "edd_classique", "files", default={})

    def get_type_habitat_advanced_display(self, nb_logements=0):
        return (
            " "
            + self.get_type_habitat_display().lower()
            + ("s" if nb_logements and nb_logements > 1 else "")
            if self.type_habitat
            else ""
        )

    def lgts_mixite_sociale_negocies_display(self):
        return self.lgts_mixite_sociale_negocies if self.mixity_option() else 0

    def mixity_option(self):
        """
        return True if the option regarding the number of lodging in addition to loan to people
        with low revenu should be displayed in the interface and fill in the convention document
        Should be editable when it is a PLUS convention
        """
        return self.financement == Financement.PLUS

    def __str__(self):
        return f"{self.programme.nom} - {self.financement}"


class Logement(models.Model):

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    designation = models.CharField(
        max_length=255, verbose_name="Désignation des logements"
    )
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    lot = models.ForeignKey(
        "Lot",
        on_delete=models.CASCADE,
        related_name="logements",
        null=False,
    )
    typologie = models.CharField(
        max_length=25,
        choices=TypologieLogement.choices,
        default=TypologieLogement.T1,
    )
    surface_habitable = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, verbose_name="Surface habitable"
    )
    surface_annexes = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    surface_annexes_retenue = models.DecimalField(
        max_digits=6, decimal_places=2, null=True
    )
    surface_utile = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, verbose_name="Surface utile"
    )
    loyer_par_metre_carre = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        verbose_name="Loyer maximum en € par m² de surface utile",
    )
    coeficient = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        verbose_name="Coefficient propre au logement",
    )
    loyer = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    import_mapping = {
        "Désignation des logements": designation,
        "Type": typologie,
        "Surface habitable\n(article R.111-2)": surface_habitable,
        "Surface des annexes\nRéelle": surface_annexes,
        "Surface des annexes\nRetenue dans la SU": surface_annexes_retenue,
        "Surface utile\n(surface habitable augmentée de 50% de la surface des annexes)": (
            surface_utile
        ),
        "Loyer maximum en € par m² de surface utile": loyer_par_metre_carre,
        "Coefficient propre au logement": coeficient,
        "Loyer maximum du logement en €\n(col 4 * col 5 * col 6)": loyer,
    }
    sheet_name = "Logements"
    needed_in_mapping = [
        designation,
        surface_habitable,
        surface_utile,
        loyer_par_metre_carre,
        coeficient,
    ]

    def __str__(self):
        return self.designation

    def _get_designation(self):
        return self.designation

    d = property(_get_designation)

    def _get_typologie(self):
        return self.get_typologie_display()

    t = property(_get_typologie)

    def _get_surface_habitable(self):
        return self.surface_habitable

    sh = property(_get_surface_habitable)

    def _get_surface_annexes(self):
        return self.surface_annexes

    sa = property(_get_surface_annexes)

    def _get_surface_annexes_retenue(self):
        return self.surface_annexes_retenue

    sar = property(_get_surface_annexes_retenue)

    def _get_surface_utile(self):
        return self.surface_utile

    su = property(_get_surface_utile)

    def _get_loyer_par_metre_carre(self):
        return self.loyer_par_metre_carre

    lpmc = property(_get_loyer_par_metre_carre)

    def _get_coeficient(self):
        return self.coeficient

    c = property(_get_coeficient)

    def _get_loyer(self):
        return self.loyer

    l = property(_get_loyer)


class Annexe(models.Model):

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    logement = models.ForeignKey(
        "Logement",
        on_delete=models.CASCADE,
        related_name="annexes",
        null=False,
    )
    typologie = models.CharField(
        max_length=25,
        choices=TypologieAnnexe.choices,
        default=TypologieAnnexe.TERRASSE,
    )
    surface_hors_surface_retenue = models.DecimalField(max_digits=6, decimal_places=2)
    loyer_par_metre_carre = models.DecimalField(max_digits=6, decimal_places=2)
    loyer = models.DecimalField(max_digits=6, decimal_places=2)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    import_mapping = {
        "Type d'annexe": typologie,
        "Désignation des logements": "logement_designation",
        "Typologie des logements": "logement_typologie",
        "Surface de l'annexe": surface_hors_surface_retenue,
        "Loyer unitaire en €": loyer_par_metre_carre,
        "Loyer maximum en €": loyer,
    }
    sheet_name = "Annexes"

    def __str__(self):
        return f"{self.typologie} - {self.logement}"

    def _get_typologie(self):
        return self.get_typologie_display()

    t = property(_get_typologie)

    def _get_logement(self):
        return self.logement

    lgt = property(_get_logement)

    def _get_surface_hors_surface_retenue(self):
        return self.surface_hors_surface_retenue

    shsr = property(_get_surface_hors_surface_retenue)

    def _get_loyer_par_metre_carre(self):
        return self.loyer_par_metre_carre

    lpmc = property(_get_loyer_par_metre_carre)

    def _get_loyer(self):
        return self.loyer

    l = property(_get_loyer)


class TypeStationnement(IngestableModel):
    pivot = ["typologie", "lot"]
    mapping = {
        "typologie": "Typologie Garage",
        "nb_stationnements": "Nb Stationnement",
        "loyer": "Loyer",
        "lot": "Produit",
        "bailleur": "MOA (code SIRET)",
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    )
    lot = models.ForeignKey(
        "Lot",
        related_name="type_stationnements",
        on_delete=models.CASCADE,
        null=False,
    )
    typologie = models.CharField(
        max_length=35,
        choices=TypologieStationnement.choices,
        default=TypologieStationnement.PLACE_STATIONNEMENT,
    )
    nb_stationnements = models.IntegerField()
    loyer = models.DecimalField(max_digits=6, decimal_places=2)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    import_mapping = {
        "Type de stationnement": typologie,
        "Nombre de stationnements": nb_stationnements,
        "Loyer maximum en €": loyer,
    }
    sheet_name = "Stationnements"

    def __str__(self):
        return f"{self.typologie} - {self.lot}"

    def _get_typologie(self):
        return self.get_typologie_display()

    t = property(_get_typologie)

    def _get_nb_stationnements(self):
        return self.nb_stationnements

    nb = property(_get_nb_stationnements)

    def _get_loyer(self):
        return self.loyer

    l = property(_get_loyer)
