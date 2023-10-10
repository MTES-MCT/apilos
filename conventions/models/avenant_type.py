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
        "prets",
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
