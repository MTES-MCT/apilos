import uuid

from django.db import models


class CommentStatut(models.TextChoices):
    # Le commentaire est ouvert par l'instructeur - Affichage en rouge
    OUVERT = "OUVERT", "Ouvert"
    # Le commentaire a été marqué comme résolu par le bailleur - Affichage en vert
    RESOLU = "RESOLU", "Résolu"
    # L'instructeur a clos le commentaire - Par d'affichage
    CLOS = "CLOS", "Commentaire clos"


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nom_objet = models.CharField(max_length=255)
    champ_objet = models.CharField(max_length=255)
    uuid_objet = models.UUIDField(max_length=255, null=True)
    convention = models.ForeignKey(
        "conventions.Convention", on_delete=models.CASCADE, null=False
    )
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False)
    message = models.TextField(null=True)
    statut = models.CharField(
        max_length=25,
        choices=CommentStatut.choices,
        default=CommentStatut.OUVERT,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)
    resolu_le = models.DateTimeField(null=True)
    clos_le = models.DateTimeField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["statut"], name="comment_statut_idx"),
        ]

    def object_detail(self):
        mapping_nom_objet = {
            "logement_edd": "Tableau de l'EDD simplifié",
            "reference_cadastrale": "Tableau des références cadastrales",
            "pret": "Tableau des prêts et financements",
            "logement": "Tableaux des logements",
            "locaux_collectifs": "Tableaux des locaux collectifs",
            "annexe": "Tableaux des annexes",
            "type_stationnement": "Tableaux des types de stationnement",
        }
        mapping_champ_objet = {
            "bailleur__uuid": "Choix du bailleur",
            "bailleur__nom": "Nom du bailleur",
            "bailleur__adresse": "Adresse du bailleur",
            "bailleur__code_postal": "Code postal du bailleur",
            "bailleur__ville": "Ville du bailleur",
            "bailleur__siret": "SIRET du bailleur",
            "bailleur__capital_social": "Capital social du bailleur",
            "bailleur__signataire_nom": "Nom du signataire du bailleur",
            "bailleur__signataire_fonction": "Fonction du signataire du bailleur",
            "bailleur__signataire_date_deliberation": (
                "Date de délibération du signataire du bailleur"
            ),
            "bailleur__signataire_bloc_signature": "Bloc signature du bailleur",
            "programme__nom": "Nom de l'opération",
            "programme__code_postal": "Code postal de l'opération",
            "programme__ville": "Ville de l'opération",
            # FIXME : should be lot__nb_logements
            "programme__nb_logements": "Nombre de logements à conventionner",
            "programme__anru": "Option ANRU de l'opération",
            "programme__nb_locaux_commerciaux": (
                "Nombre de locaux commerciaux de l'opération"
            ),
            "programme__nb_bureaux": "Nombre de bureaux de l'opération",
            "programme__autres_locaux_hors_convention": "Autre locaux de l'opération",
            "programme__type_operation": "Type d'opération",
            "programme__type_habitat": "Type d'habitat de l'opération",
            "programme__permis_construire": "Permis de construire de l'opération",
            "programme__date_acte_notarie": "Date de l'acte notarié de l'opération",
            "programme__date_autorisation_hors_habitat_inclusif": (
                "Date d'autorisation hors habitat inclusif"
            ),
            "programme__date_convention_location": "Date de la convention de location",
            "programme__date_achat": "Date d'achat telle qu'indiquée sur l'acte notarié",
            "programme__date_achevement_previsible": (
                "Date d'achèvement prévisible de l'opération"
            ),
            "programme__date_achevement": (
                "Date d'achèvement ou d'obtention de certificat de conformité de"
                + " l'opération"
            ),
            "programme__vendeur": "Vendeur tel qu'indiqué sur l'acte notarié",
            "programme__acquereur": "Acquéreur tel qu'indiqué sur l'acte notarié",
            "programme__reference_notaire": (
                "Référence du notaire tel qu'indiqué sur l'acte notarié"
            ),
            "programme__reference_publication_acte": (
                "Référence de publication de l'acte notarié"
            ),
            "programme__acte_de_propriete": "Acte de propriété ou acte notarial",
            "programme__certificat_adressage": "Certificat d'adressage ou autres",
            "programme__effet_relatif": "Effet relatif de l'opération",
            "programme__reference_cadastrale": (
                "Références cadastrales de l'opération"
            ),
            "convention__annee_fin_conventionnement": "Date de fin de la convention",
            "convention__fond_propre": "Fonds propres finançant l'opération",
            "lot__loyer_derogatoire": "Loyer dérogatoire des logements",
            "lot__surface_locaux_collectifs_residentiels": "Surface des locaux collectifs résidentiels",
            "lot__lgts_mixite_sociale_negocies": "Option de mixité sociale négociée",
            "lot__annexe_caves": "Option caves dans les annexes",
            "lot__annexe_soussols": "Option sous-sol dans les annexes",
            "lot__annexe_remises": "Option remises dans les annexes",
            "lot__annexe_ateliers": "Option ateliers dans les annexes",
            "lot__annexe_sechoirs": "Option séchoirs dans les annexes",
            "lot__annexe_celliers": "Option celliers extérieurs au logement dans les annexes",
            "lot__annexe_resserres": "Option resserres dans les annexes",
            "lot__annexe_combles": "Option combles et greniers aménageables dans les annexes",
            "lot__annexe_balcons": "Option balcons dans les annexes",
            "lot__annexe_loggias": "Option loggias et vérandas dans les annexes",
            "lot__annexe_terrasses": "Option terrasses dans les annexes",
            "convention__commentaires": "Commentaires à l'attention de l'instructeur",
            "lot__edd_volumetrique": "EDD volumétrique",
            "lot__edd_classique": "EDD classique",
            "programme__edd_stationnements": "EDD pour les stationnements",
            "programme__mention_publication_edd_volumetrique": (
                "Mention de publication de l'edd volumétrique"
            ),
            "programme__mention_publication_edd_classique": (
                "Mention de publication de l'edd classique"
            ),
            "convention__adresse": "Adresse de l'opération",
            "convention__type1and2": "Selection du type I ou II de la convention",
            "convention__type2_lgts_concernes_option1": (
                "Option 1 pour les convention de type II"
            ),
            "convention__type2_lgts_concernes_option2": (
                "Option 2 pour les convention de type II"
            ),
            "convention__type2_lgts_concernes_option3": (
                "Option 3 pour les convention de type II"
            ),
            "convention__type2_lgts_concernes_option4": (
                "Option 4 pour les convention de type II"
            ),
            "convention__type2_lgts_concernes_option5": (
                "Option 5 pour les convention de type II"
            ),
            "convention__type2_lgts_concernes_option6": (
                "Option 6 pour les convention de type II"
            ),
            "convention__type2_lgts_concernes_option7": (
                "Option 7 pour les convention de type II"
            ),
            "convention__type2_lgts_concernes_option8": (
                "Option 8 pour les convention de type II"
            ),
            "convention__gestionnaire": "Entreprise gestionnaire",
            "convention__gestionnaire_signataire_nom": (
                "Nom du signataire du gestionnaire"
            ),
            "convention__gestionnaire_signataire_fonction": (
                "Fonction du signataire du gestionnaire"
            ),
            "convention__gestionnaire_signataire_date_deliberation": (
                "Date de délibération du signataire du gestionnaire"
            ),
            "convention__gestionnaire_signataire_bloc_signature": (
                "Bloc signature du gestionnaire"
            ),
            "lot__foyer_residence_nb_garage_parking": "Garages et/ ou parking (nombre)",
            "lot__foyer_residence_dependance": "Dépendances (nombre et surface)",
            "lot__foyer_residence_locaux_hors_convention": (
                "Locaux auxquels ne s'appliquent pas la convention (Liste)"
            ),
            "convention__attribution_inclusif_conditions_specifiques": (
                "Conditions spécifiques d'accueil"
            ),
            "convention__attribution_inclusif_conditions_admission": (
                "Conditions d'admission dans l’habitat inclusif"
            ),
            "convention__attribution_inclusif_modalites_attribution": "Modalités d'attribution",
            "convention__attribution_inclusif_partenariats": "Partenariats",
            "convention__attribution_inclusif_activites": "Activités proposées",
            "convention__attribution_modalites_reservations": (
                "Modalités de gestion des reservations"
            ),
            "convention__attribution_modalites_choix_personnes": (
                "Modalités de choix des personnes accueillies"
            ),
            "convention__attribution_prestations_integrees": (
                "Prestation intégrées dans la redevance"
            ),
            "convention__attribution_prestations_facultatives": "Prestations facultatives",
            "convention__attribution_reservation_prefectorale": (
                "Part de réservations préfectorales"
            ),
            "convention__foyer_residence_variante_1": "Variante 1",
            "convention__foyer_residence_variante_2": "Variante 2",
            "convention__foyer_residence_variante_2_travaux": "Variante 2 travaux",
            "convention__foyer_residence_variante_2_nb_tranches": "Variante 2 nombre de tranches",
            "convention__foyer_residence_variante_2_nb_annees": "Variante 2 nombre d'annees",
            "convention__foyer_residence_variante_3": "Variante 3",
            "convention__attached": "Fichiers à joindre à la convention",
            "convention__attribution_agees_autonomie": "Résidence autonomie",
            "convention__attribution_agees_ephad": (
                "Établissement hébergeant des personnes âgées dépendantes (EHPAD)"
            ),
            "convention__attribution_agees_desorientees": (
                "Unité pour personnes désorientées (unités Alzheimer, ...)"
            ),
            "convention__attribution_agees_petite_unite": (
                "Petite unité de vie (établissement de moins de 25 places autorisées)"
            ),
            "convention__attribution_agees_autre": "Autres",
            "convention__attribution_agees_autre_detail": "Autres",
            "convention__attribution_handicapes_foyer": "Foyer",
            "convention__attribution_handicapes_foyer_de_vie": "Foyer de vie ou occupationnel",
            "convention__attribution_handicapes_foyer_medicalise": "Foyer d'accueil médicalisé",
            "convention__attribution_handicapes_autre": "Autres",
            "convention__attribution_handicapes_autre_detail": "Autres [préciser]",
        }
        if f"{self.nom_objet}__{self.champ_objet}" in mapping_champ_objet:
            return mapping_champ_objet[f"{self.nom_objet}__{self.champ_objet}"]
        if self.nom_objet in mapping_nom_objet:
            return mapping_nom_objet[self.nom_objet]

        return f"{self.nom_objet} - {self.champ_objet}"
