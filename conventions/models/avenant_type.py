from django.db import models

AVENANT_TYPE_FIELDS_MAPPING = {
    "denonciation": [
        "date_denonciation",
        "motif_denonciation",
        "fichier_instruction_denonciation",
    ],
    "logements": [
        "lot.logements",
        "lot.loyer_derogatoire",
        "lot.surface_locaux_collectifs_residentiels",
        "lot.loyer_associations_foncieres",
        "lot.annexe_caves",
        "lot.annexe_soussols",
        "lot.annexe_remises",
        "lot.annexe_ateliers",
        "lot.annexe_sechoirs",
        "lot.annexe_celliers",
        "lot.annexe_resserres",
        "lot.annexe_combles",
        "lot.annexe_balcons",
        "lot.annexe_loggias",
        "lot.annexe_terrasses",
        "lot.surface_habitable_totale",
        "lot.locaux_collectifs",
        "lot.foyer_residence_nb_garage_parking",
        "lot.foyer_residence_dependance",
        "lot.foyer_residence_locaux_hors_convention",
    ],
    "champ_libre": [
        "champ_libre_avenant",
    ],
    "programme": [
        "programme.nom",
        "adresse",
    ],
    "commentaires": [
        "commentaires",
    ],
    "duree": [
        "lot.prets",
        "date_fin_conventionnement",
        "fond_propre",
        "historique_financement_public",
    ],
    "bailleur": [
        "programme.bailleur",
        "programme.administration",
        "signataire_nom",
        "signataire_fonction",
        "signataire_date_deliberation",
        "signataire_bloc_signature",
        "gestionnaire",
        "gestionnaire_signataire_nom",
        "gestionnaire_signataire_fonction",
        "gestionnaire_signataire_date_deliberation",
    ],
    "edd": [
        "programme.edd_volumetrique",
        "programme.mention_publication_edd_volumetrique",
        "programme.edd_classique",
        "programme.mention_publication_edd_classique",
        "programme.logementedds",
    ],
    "residence_attribution": [
        "attribution_residence_sociale_ordinaire",
        "attribution_pension_de_famille",
        "attribution_residence_accueil",
        "attribution_modalites_reservations",
        "attribution_modalites_choix_personnes",
        "attribution_prestations_integrees",
        "attribution_prestations_facultatives",
    ],
    "foyer_attribution": [
        "attribution_agees_autonomie",
        "attribution_agees_ephad",
        "attribution_agees_desorientees",
        "attribution_agees_petite_unite",
        "attribution_agees_autre",
        "attribution_agees_autre_detail",
        "attribution_handicapes_foyer",
        "attribution_handicapes_foyer_de_vie",
        "attribution_handicapes_foyer_medicalise",
        "attribution_handicapes_autre",
        "attribution_handicapes_autre_detail",
        "attribution_inclusif_conditions_specifiques",
        "attribution_inclusif_conditions_admission",
        "attribution_inclusif_modalites_attribution",
        "attribution_inclusif_partenariats",
        "attribution_inclusif_activites",
        "attribution_modalites_reservations",
        "attribution_modalites_choix_personnes",
        "attribution_prestations_integrees",
        "attribution_prestations_facultatives",
    ],
    "variantes": [
        "foyer_residence_variante_1",
        "foyer_residence_variante_2",
        "foyer_residence_variante_2_travaux",
        "foyer_residence_variante_2_nb_tranches",
        "foyer_residence_variante_2_nb_annees",
        "foyer_residence_variante_3",
    ],
    "stationnement": [
        "lot.type_stationnements",
    ],
    "cadastre": [
        "programme.date_convention_location",
        "programme.date_autorisation_hors_habitat_inclusif",
        "programme.departement_residence_argement_gestionnaire_intermediation",
        "programme.ville_signature_residence_agrement_gestionnaire_intermediation",
        "programme.date_residence_argement_gestionnaire_intermediation",
        "programme.date_achat",
        "programme.date_acte_notarie",
        "programme.date_achevement",
        "programme.date_achevement_previsible",
        "programme.vendeur",
        "programme.acquereur",
        "programme.reference_notaire",
        "programme.reference_publication_acte",
        "programme.reference_cadastrale",
        "programme.referencecadastrales",
    ],
}


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

    @property
    def fields(self):
        return AVENANT_TYPE_FIELDS_MAPPING.get(self.nom) or []

    class Meta:
        indexes = [
            models.Index(fields=["nom"], name="avenant_type_nom_idx"),
        ]
