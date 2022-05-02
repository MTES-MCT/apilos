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

    def object_detail(self):
        mapping_nom_objet = {
            "logement_edd": "Tableau de l'EDD simplifié",
            "reference_cadastrale": "Tableau des références cadastrales",
            "pret": "Tableau des prêts et financements",
            "logement": "Tableaux des logements",
            "annexe": "Tableaux des annexes",
            "type_stationnement": "Tableaux des types de stationnement",
        }
        mapping_champ_objet = {
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
            "programme__nom": "Nom de l'opération",
            "programme__adresse": "Adresse de l'opération",
            "programme__code_postal": "Code postal de l'opération",
            "programme__ville": "Ville de l'opération",
            "programme__nb_logements": "Nombre de logements à conventionner",
            "programme__anru": "Option ANRU de l'opération",
            "programme__nb_locaux_commerciaux": "Nombre de locaux commerciaux de l'opération",
            "programme__nb_bureaux": "Nombre de bureaux de l'opération",
            "programme__autres_locaux_hors_convention": "Autre locaux de l'opération",
            "programme__type_operation": "Type d'opération",
            "programme__type_habitat": "Type d'habitat de l'opération",
            "programme__permis_construire": "Permis de construire de l'opération",
            "programme__date_acte_notarie": "Date de l'acte notarié de l'opération",
            "programme__date_achat": "Date d'achat telle qu'indiquée sur l'acte notarié",
            "programme__date_achevement_previsible": "Date d'achèvement prévisible de l'opération",
            "programme__date_achevement": (
                "Date d'achèvement ou d'obtention de certificat de conformité de l'opération"
            ),
            "programme__vendeur": "Vendeur tel qu'indiqué sur l'acte notarié",
            "programme__acquereur": "Acquéreur tel qu'indiqué sur l'acte notarié",
            "programme__reference_notaire": (
                "Référence du notaire tel qu'indiqué sur l'acte notarié"
            ),
            "programme__reference_publication_acte": "Référence de publication de l'acte notarié",
            "programme__acte_de_propriete": "Acte de propriété ou acte notarial",
            "programme__certificat_adressage": "Certificat d'adressage ou autres",
            "programme__reference_cadastrale": (
                "Références cadastrales et effet relatif de l'opération"
            ),
            "convention__annee_fin_conventionnement": "Date de fin de la convention",
            "convention__fond_propre": "Fonds propres finançant l'opération",
            "lot__loyer_derogatoire": "Loyer dérogatoire des logements",
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
            "convention__comments": "Commentaires à l'attention de l'instructeur",
            "lot__edd_volumetrique": "EDD volumétrique",
            "lot__edd_classique": "EDD classique",
            "programme__mention_publication_edd_volumetrique": (
                "Mention de publication de l'edd volumétrique"
            ),
            "programme__mention_publication_edd_classique": (
                "Mention de publication de l'edd classique"
            ),
        }
        if f"{self.nom_objet}__{self.champ_objet}" in mapping_champ_objet:
            return mapping_champ_objet[f"{self.nom_objet}__{self.champ_objet}"]
        if self.nom_objet in mapping_nom_objet:
            return mapping_nom_objet[self.nom_objet]

        return f"{self.nom_objet} - {self.champ_objet}"
