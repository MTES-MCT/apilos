import logging
import uuid
from typing import Any

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import model_to_dict

from apilos_settings.models import Departement
from conventions.models.choices import ConventionStatut
from core.models import IngestableModel
from core.utils import get_key_from_json_field

from .choices import (
    Financement,
    FinancementEDD,
    NatureLogement,
    TypeHabitat,
    TypeOperation,
    TypologieAnnexe,
    TypologieLogement,
    TypologieStationnement,
    Zone123,
    ZoneABC,
)

logger = logging.getLogger(__name__)


class Programme(IngestableModel):
    class Meta:
        indexes = [
            models.Index(fields=["numero_galion"], name="programme_numero_galion_idx"),
            models.Index(fields=["ville"], name="programme_ville_idx"),
            models.Index(fields=["code_postal"], name="programme_code_postal_idx"),
            models.Index(fields=["nom"], name="programme_nom_idx"),
            models.Index(fields=["-date_achevement_compile"]),
        ]

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
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    numero_galion = models.CharField(max_length=255, null=True)
    bailleur = models.ForeignKey(
        "bailleurs.Bailleur",
        on_delete=models.CASCADE,
        null=False,
    )
    administration = models.ForeignKey(
        "instructeurs.Administration", on_delete=models.SET_NULL, null=True
    )
    adresse = models.TextField(null=True, blank=True)
    code_postal = models.CharField(max_length=5, null=True, blank=True)
    ville = models.CharField(max_length=255, null=True, blank=True)
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
        max_digits=10, decimal_places=2, null=True
    )
    surface_corrigee_totale = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
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
    mention_publication_edd_volumetrique = models.TextField(max_length=5000, null=True)
    edd_classique = models.TextField(max_length=5000, null=True)
    mention_publication_edd_classique = models.TextField(max_length=5000, null=True)
    edd_stationnements = models.TextField(max_length=5000, null=True, blank=True)
    permis_construire = models.CharField(max_length=255, null=True)
    date_achevement_previsible = models.DateField(null=True)
    date_achat = models.DateField(null=True)
    date_achevement = models.DateField(null=True)
    date_autorisation_hors_habitat_inclusif = models.DateField(null=True)  # FOYER
    date_convention_location = models.DateField(null=True)  # FOYER & RESIDENCE

    date_residence_argement_gestionnaire_intermediation = models.DateField(
        null=True
    )  # RESIDENCE
    departement_residence_argement_gestionnaire_intermediation = models.CharField(
        null=True, max_length=255
    )  # RESIDENCE
    ville_signature_residence_agrement_gestionnaire_intermediation = models.CharField(
        null=True, max_length=255
    )  # RESIDENCE

    date_achevement_compile = models.DateField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    @property
    def all_conventions_are_signed(self):
        not_signed_conventions = [
            convention
            for convention in self.all_conventions
            if convention.statut
            in [
                ConventionStatut.PROJET.label,
                ConventionStatut.INSTRUCTION.label,
                ConventionStatut.CORRECTION.label,
                ConventionStatut.A_SIGNER.label,
            ]
        ]
        return not not_signed_conventions

    @property
    def last_conventions_state(self):
        conventions_by_financement = {}
        conventions = [
            convention
            for convention in self.all_conventions
            if convention.statut
            not in [
                ConventionStatut.PROJET.label,
                ConventionStatut.INSTRUCTION.label,
                ConventionStatut.CORRECTION.label,
                ConventionStatut.A_SIGNER.label,
            ]
        ]
        for convention in conventions:
            if (
                convention.financement not in conventions_by_financement
                or conventions_by_financement[convention.financement].cree_le
                < convention.cree_le
            ):
                conventions_by_financement[convention.financement] = convention

        # filter last signed one by fianncement
        return [convention for _, convention in conventions_by_financement.items()]

    @property
    def all_conventions(self):
        return [
            convention
            for programme in Programme.objects.filter(
                numero_galion=self.numero_galion
            ).all()
            for convention in programme.conventions.all()
        ]

    def __str__(self):
        return self.nom

    def clone(self):
        parent_id = self.parent_id or self.id
        programme_fields = model_to_dict(
            self,
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
                "parent_id": parent_id,
            }
        )
        cloned_programme = Programme(**programme_fields)
        cloned_programme.save()
        return cloned_programme

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
        return get_key_from_json_field(self.vendeur, "text")

    def vendeur_files(self):
        return get_key_from_json_field(self.vendeur, "files", default={})

    def acquereur_text(self):
        return get_key_from_json_field(self.acquereur, "text")

    def acquereur_files(self):
        return get_key_from_json_field(self.acquereur, "files", default={})

    def reference_notaire_text(self):
        return get_key_from_json_field(self.reference_notaire, "text")

    def reference_notaire_files(self):
        return get_key_from_json_field(self.reference_notaire, "files", default={})

    def reference_publication_acte_text(self):
        return get_key_from_json_field(self.reference_publication_acte, "text")

    def reference_publication_acte_files(self):
        return get_key_from_json_field(
            self.reference_publication_acte, "files", default={}
        )

    def acte_de_propriete_files(self):
        return get_key_from_json_field(self.acte_de_propriete, "files", default={})

    def certificat_adressage_files(self):
        return get_key_from_json_field(self.certificat_adressage, "files", default={})

    def effet_relatif_files(self):
        return get_key_from_json_field(self.effet_relatif, "files", default={})

    def reference_cadastrale_files(self):
        return get_key_from_json_field(self.reference_cadastrale, "files", default={})

    def edd_volumetrique_text(self):
        return get_key_from_json_field(self.edd_volumetrique, "text")

    def edd_volumetrique_files(self):
        return get_key_from_json_field(self.edd_volumetrique, "files", default={})

    def edd_classique_text(self):
        return get_key_from_json_field(self.edd_classique, "text")

    def edd_classique_files(self):
        return get_key_from_json_field(self.edd_classique, "files", default={})

    def edd_stationnements_text(self):
        return get_key_from_json_field(self.edd_stationnements, "text")

    def edd_stationnements_files(self):
        return get_key_from_json_field(self.edd_stationnements, "files", default={})

    def is_foyer(self):
        return self.nature_logement in [NatureLogement.AUTRE]

    def is_residence(self):
        return self.nature_logement in [
            NatureLogement.HEBERGEMENT,
            NatureLogement.RESISDENCESOCIALE,
            NatureLogement.PENSIONSDEFAMILLE,
            NatureLogement.RESIDENCEDACCUEIL,
        ]


@receiver(pre_save, sender=Programme)
def compute_date_achevement_compile(sender, instance, *args, **kwargs):
    instance.date_achevement_compile = (
        instance.date_achevement or instance.date_achevement_previsible
    )
    if instance.code_postal and len(instance.code_postal) == 5:
        code_departement = instance.code_postal[0:2]
        if (
            instance.code_insee_departement != code_departement
            and instance.code_insee_departement
            not in [
                "2A",
                "2B",
            ]
        ):
            try:
                if code_departement == "20":
                    # Cas spécial de la Corse car in n'est pas possible de déterminer le département
                    # à partir du code postal
                    departement = Departement.objects.filter(
                        code_postal=code_departement
                    ).first()
                    if departement:
                        instance.code_insee_departement = "20"
                        instance.code_insee_region = departement.code_insee_region
                else:
                    departement = Departement.objects.get(code_postal=code_departement)
                    instance.code_insee_departement = departement.code_insee
                    instance.code_insee_region = departement.code_insee_region
            except (Departement.DoesNotExist, AttributeError):
                logger.error(
                    "Le numero de departement %s n'existe pas depuis le code postal %s",
                    code_departement,
                    instance.code_postal,
                )


class LogementEDD(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    designation = models.CharField(max_length=255)
    programme = models.ForeignKey(
        "Programme", on_delete=models.CASCADE, null=False, related_name="logementedds"
    )
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

    # Needed for admin
    @property
    def bailleur(self):
        return self.programme.bailleur

    def __str__(self):
        return self.designation


class ReferenceCadastrale(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    programme = models.ForeignKey(
        "Programme",
        on_delete=models.CASCADE,
        null=False,
        related_name="referencecadastrales",
    )
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

    # Needed for admin
    @property
    def bailleur(self):
        return self.programme.bailleur

    @staticmethod
    def compute_surface(superficie: int | None = None):
        s = superficie if superficie is not None else 0

        return f"{s // 10000} ha {(s % 10000) // 100} a {s % 100} ca"

    def __str__(self):
        return f"{self.section} - {self.numero} - {self.lieudit}"


class RepartitionSurface(models.Model):
    """
    Répartition du nombre de logements par typologie de surface (T1, T2, etc...)
    et type d'habitat (individuel ou collectif).

    Ces informations étaient déclarées dans Ecoloweb et ne sont donc destinées qu'à un
    usage consultatif.
    """

    class Meta:
        unique_together = ("lot", "typologie", "type_habitat")

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    lot = models.ForeignKey(
        "Lot",
        on_delete=models.CASCADE,
        null=False,
        related_name="surfaces",
    )
    typologie = models.CharField(
        max_length=25,
        choices=TypologieLogement.choices,
        default=TypologieLogement.T1,
    )
    type_habitat = models.CharField(
        max_length=25,
        choices=filter(lambda th: th[0] != TypeHabitat.MIXTE, TypeHabitat.choices),
        default=TypeHabitat.INDIVIDUEL,
    )
    quantite = models.IntegerField()


class Lot(IngestableModel):
    pivot = ["financement", "programme", "type_habitat"]
    mapping = {
        "financement": "Produit",
        "programme": "Nom Opération",
        "nb_logements": "Nb logts",
        "type_habitat": "Type d'habitat",
    }

    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nb_logements = models.IntegerField(null=True)
    programme = models.ForeignKey(
        "Programme", on_delete=models.CASCADE, null=False, related_name="lots"
    )
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
    surface_habitable_totale = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    surface_locaux_collectifs_residentiels = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        blank=True,
        verbose_name="Surface des locaux collectifs résidentiels",
    )
    foyer_residence_nb_garage_parking = models.IntegerField(blank=True, null=True)
    foyer_residence_dependance = models.TextField(
        max_length=5000, blank=True, null=True
    )
    foyer_residence_locaux_hors_convention = models.TextField(
        max_length=5000, blank=True, null=True
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    # Needed for admin
    @property
    def bailleur(self):
        return self.programme.bailleur

    @property
    def annexes(self):
        return Annexe.objects.filter(logement__lot=self)

    def clone(self, cloned_programme):
        parent_id = self.parent_id or self.id
        lot_fields = model_to_dict(
            self,
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
                "parent_id": parent_id,
            }
        )
        cloned_lot = Lot(**lot_fields)
        cloned_lot.save()
        return cloned_lot

    def repartition_surfaces(self):
        """
        Construit un dictionnaire à 2 niveaux TypeHabitat<Typologie<int>> détaillant le
        nombre de logements par type d'habitat et typologie de logement, ou 0 si no renseigné.
        """
        return dict(
            (
                type_habitat,
                dict(
                    (
                        typologie,
                        self.surfaces.filter(
                            type_habitat=type_habitat, typologie=typologie
                        )
                        .values_list("quantite", flat=True)
                        .first()
                        or 0,
                    )
                    for typologie, _1 in TypologieLogement.choices
                ),
            )
            for type_habitat, _2 in filter(
                lambda th: th[0] != TypeHabitat.MIXTE, TypeHabitat.choices
            )
        )

    def edd_volumetrique_text(self):
        return get_key_from_json_field(self.edd_volumetrique, "text")

    def edd_volumetrique_files(self):
        return get_key_from_json_field(self.edd_volumetrique, "files", default={})

    def edd_classique_text(self):
        return get_key_from_json_field(self.edd_classique, "text")

    def edd_classique_files(self):
        return get_key_from_json_field(self.edd_classique, "files", default={})

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
        return self.financement in [Financement.PLUS, Financement.PLUS_CD]

    def __str__(self):
        return f"{self.programme.nom} - {self.financement}"


class Logement(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    designation = models.CharField(
        max_length=255, verbose_name="Désignation des logements"
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
        max_digits=12, decimal_places=2, null=True, verbose_name="Surface habitable"
    )
    surface_corrigee = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, verbose_name="Surface corrigée"
    )
    surface_annexes = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    surface_annexes_retenue = models.DecimalField(
        max_digits=12, decimal_places=2, null=True
    )
    surface_utile = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, verbose_name="Surface utile"
    )
    loyer_par_metre_carre = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        verbose_name="Loyer maximum en € par m² de surface utile",
    )
    coeficient = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        verbose_name="Coefficient propre au logement",
    )
    loyer = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    import_mapping = {
        "Désignation des logements": designation,
        "Type": typologie,
        "Surface habitable\n(article": surface_habitable,
        "Surface des annexes\nRéelle": surface_annexes,
        "Surface des annexes\nRetenue dans la SU": surface_annexes_retenue,
        "Surface utile\n(surface habitable augmentée de 50% de la surface des annexes)": (
            surface_utile
        ),
        "Loyer maximum en € par m² de surface utile": loyer_par_metre_carre,
        "Coefficient propre au logement": coeficient,
        "Loyer maximum du logement en €\n(col 4 * col 5 * col 6)": loyer,
    }

    foyer_residence_import_mapping = {
        "Numéro du logement": designation,
        "Type": typologie,
        "Surface habitable": surface_habitable,
        "Redevance maximale": loyer,
    }

    sheet_name = "Logements"
    needed_in_mapping = [
        designation,
        surface_habitable,
        surface_utile,
        loyer_par_metre_carre,
        coeficient,
    ]
    foyer_residence_needed_in_mapping = [
        designation,
        typologie,
        surface_habitable,
        loyer,
    ]

    # Needed for admin
    @property
    def bailleur(self):
        return self.lot.programme.bailleur

    def clone(self, lot: Lot, **kwargs: dict[str, Any]) -> "Logement":
        logement_fields = (
            model_to_dict(
                self,
                exclude=[
                    "uuid",
                    "id",
                    "cree_le",
                    "mis_a_jour_le",
                ],
            )
            | {"lot": lot}
            | kwargs
        )
        cloned_logement = Logement.objects.create(**logement_fields)

        for annexe in self.annexes.all():
            annexe.clone(cloned_logement)

        return cloned_logement

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

    l = property(_get_loyer)  # noqa: E741


class Annexe(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
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

    # Needed for admin
    @property
    def bailleur(self):
        return self.logement.lot.programme.bailleur

    def clone(self, cloned_logement, **kwargs):
        annexe_fields = model_to_dict(
            self,
            exclude=[
                "uuid",
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

    l = property(_get_loyer)  # noqa: E741


class LocauxCollectifs(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    lot = models.ForeignKey(
        "Lot",
        on_delete=models.CASCADE,
        related_name="locaux_collectifs",
        null=False,
    )

    type_local = models.CharField(max_length=255)
    surface_habitable = models.DecimalField(max_digits=6, decimal_places=2)
    nombre = models.IntegerField()

    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    import_mapping = {
        "Type de local": type_local,
        "Surface habitable": surface_habitable,
        "Nombre": nombre,
    }
    sheet_name = "Locaux Collectifs"


class TypeStationnement(IngestableModel):
    pivot = ["typologie", "lot"]
    mapping = {
        "typologie": "Typologie Garage",
        "nb_stationnements": "Nb Stationnement",
        "loyer": "Loyer",
        "lot": "Produit",
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
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

    # Needed for admin
    @property
    def bailleur(self):
        return self.lot.programme.bailleur

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

    l = property(_get_loyer)  # noqa: E741


class IndiceEvolutionLoyer(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=["annee", "is_loyer", "nature_logement"],
                name="idx_annee_and_type",
            ),
        ]

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    is_loyer = models.BooleanField(default=True)
    annee = models.IntegerField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    nature_logement = models.TextField(
        choices=NatureLogement.choices,
        default=NatureLogement.LOGEMENTSORDINAIRES,
        null=True,
    )
    # Evolution, en pourcentage
    evolution = models.FloatField()

    def __str__(self):
        return f"{self.annee} / {self.nature_logement} => {self.evolution}"
