from enum import Enum
from typing import NamedTuple

from django.db.models import TextChoices


class StatutByRole(NamedTuple):
    label: str
    description_entete: str | None = ""


class ReverseEnumMixin:
    _reverse: dict = {}

    @classmethod
    def get_by_label(cls, label: str | None) -> Enum | None:
        if not label:
            return None
        if not cls._reverse:
            cls._reverse = {c.label: c for c in cls}
        try:
            return cls._reverse[label]
        except KeyError:
            return None


class ConventionStatut(ReverseEnumMixin, Enum):
    """
    A/ PROJET : Projet - Création d'un projet de convention
        Le bailleur crée un projet de convention APL, il ajoute à ce projet des documents
        et des informations concernant les logements de l'opération.
        Anciennement BROUILLON

    B/ Instruction (2 sous-statuts) : Instruction du projet de convention
        Le bailleur et l'instructeur échangent et s'alignent sur le contenu de la convention

        B1/ INSTRUCTION : Instruction requise - Projet de convention soumis à l'instruction
            L'instructeur vérifie le contenu du projet de convention et, si nécessaire,
            transmet au bailleur ses demandes de modifications
            Anciennement INSTRUCTION

        B2/ CORRECTION : Corrections requises - Projet de convention à modifier par le bailleur
            Le bailleur intègre les demandes de modification et soumet à nouveau le projet de
            convention à l'instructeur
            Anciennement CORRECTION

    C/ A_SIGNER : A signer - Convention à signer
        Le bailleur et l'instructeur sont d'accord sur le projet de convention. Les parties
        procèdent à la signature.
        Anciennement VALIDE

    D/ SIGNEE : Signée - Convention signée
        La convention signée est mise à disposition via la plateforme APiLos.
        Anciennement CLOS

    E/ RESILIEE: Résilié - Convention résiliée

    F/ DENONCEE: Dénoncée - Convention dénoncée
        Le bailleur décide, une fois la période de couverture de la convention achevée, de
        dénoncer la convention et rendre ainsi caduques toutes les clauses d'encadrement qui
        y étaient définies. Il est seul décideur, cependant depuis peu une commune considérée
        comme en "carence" de logement social peut s'opposer à cette dénonciation.

    G/ ANNULEE: Annulée en suivi - Convention annulée
        Les 2 parties s'entendent pour annuler la convention

    """

    _ignore_ = "Definition"

    class Definition(NamedTuple):
        label: str
        bailleur: StatutByRole
        instructeur: StatutByRole
        icone: str

    PROJET = Definition(
        "1. Projet",
        StatutByRole(
            "En projet",
            "Complétez ses informations, puis soumettez-{article} à votre service d'instruction",
        ),
        StatutByRole(
            "En projet",
            "Une fois que votre bailleur aura complété ses informations, il vous {article} soumettra en instruction",
        ),
        "pencil",
    )

    INSTRUCTION = Definition(
        "2. Instruction requise",
        StatutByRole(
            "En instruction",
            "{pronom} sera prochainement validé{accord} ou votre instructeur vous demandera des corrections",
        ),
        StatutByRole(
            "À instruire",
            "Vous pouvez désormais procéder à son instruction et "
            "{article} valider ou demander des corrections à votre bailleur",
        ),
        "eye",
    )
    CORRECTION = Definition(
        "3. Corrections requises",
        StatutByRole(
            "À corriger",
            "Corrigez les demandes de votre instructeur puis soumettez-{article} à nouveau",
        ),
        StatutByRole(
            "En correction",
            "Une fois que votre bailleur aura procédé aux corrections, il pourra vous {article} soumettre à nouveau",
        ),
        "question-answer",
    )
    A_SIGNER = Definition(
        "4. A signer",
        StatutByRole("À signer"),
        StatutByRole("À signer"),
        "draft",
    )
    SIGNEE = Definition(
        "5. Signée",
        StatutByRole(
            "Finalisée",
            "Vous devrez désormais créer un {autre} avenant si vous souhaitez mettre à jour une information",
        ),
        StatutByRole(
            "Finalisée",
            "Un {autre} avenant devra désormais être créé pour mettre à jour une information",
        ),
        "success",
    )
    RESILIEE = Definition(
        "6. Résiliée",
        StatutByRole(
            "Résiliée",
            "Il n'est pas possible d'y apporter des modifications",
        ),
        StatutByRole(
            "Résiliée",
            "Il n'est pas possible d'y apporter des modifications",
        ),
        "close",
    )
    DENONCEE = Definition(
        "7. Dénoncée",
        StatutByRole(
            "Dénoncée",
            "Il n'est pas possible d'y apporter des modifications",
        ),
        StatutByRole(
            "Dénoncée",
            "Il n'est pas possible d'y apporter des modifications",
        ),
        "close",
    )
    ANNULEE = Definition(
        "8. Annulée en suivi",
        StatutByRole(
            "Annulée en suivi",
            "Il n'est pas possible d'y apporter des modifications",
        ),
        StatutByRole(
            "Annulée en suivi",
            "Il n'est pas possible d'y apporter des modifications",
        ),
        "close",
    )

    @classmethod
    @property
    def choices(cls) -> list[tuple[str, str]]:
        return [(member.name, member.label) for member in cls]

    @classmethod
    def active_statuts(cls, flat: bool = True, as_instructeur: bool = True):
        if flat:
            return [
                statut.label
                for statut in [
                    cls.PROJET,
                    cls.INSTRUCTION,
                    cls.CORRECTION,
                    cls.A_SIGNER,
                ]
            ]

        return [
            (
                statut.name,
                statut.value.instructeur.label
                if as_instructeur
                else statut.value.bailleur.label,
            )
            for statut in [cls.PROJET, cls.INSTRUCTION, cls.CORRECTION, cls.A_SIGNER]
        ]

    @classmethod
    def completed_statuts(cls, flat: bool = True, as_instructeur: bool = True):
        if flat:
            return [
                statut.label
                for statut in [cls.SIGNEE, cls.RESILIEE, cls.DENONCEE, cls.ANNULEE]
            ]

        return [
            (
                statut.name,
                statut.value.instructeur.label
                if as_instructeur
                else statut.value.bailleur.label,
            )
            for statut in [cls.SIGNEE, cls.RESILIEE, cls.DENONCEE, cls.ANNULEE]
        ]

    @property
    def label(self):
        return self.value.label

    @property
    def bailleur_label(self):
        return self.value.bailleur.label

    @property
    def instructeur_label(self):
        return self.value.instructeur.label

    @property
    def icone(self):
        return self.value.icone


class ConventionType1and2(TextChoices):
    TYPE1 = "Type1", "Type I"
    TYPE2 = "Type2", "Type II"


class Preteur(TextChoices):
    ETAT = "ETAT", "Etat"
    EPCI = "EPCI", "EPCI"
    REGION = "REGION", "Région"
    VILLE = "VILLE", "Ville"
    CDCF = "CDCF", "CDC pour le foncier"
    CDCL = "CDCL", "CDC pour le logement"
    COMMUNE = "COMMUNE", "Commune et action logement"
    ANRU = "ANRU", "ANRU"
    AUTRE = "AUTRE", "Autre/Subventions"


class TypeEvenement(TextChoices):
    DEPOT_BAILLEUR = "DEPOT_BAILLEUR", "Dépôt de la convention APL par le bailleur"
    MODIFICATION = (
        "MODIFICATION",
        "Modification de la convention (valeur du loyer plafond, surface,"
        "clauses, etc...)",
    )
    ECHANGE = (
        "ECHANGE",
        "Echanges téléphoniques, électroniques ou transmission par courrier"
        "de la convention APL au bailleur",
    )
    ENVOI_PREFET = (
        "ENVOI_PREFET",
        "Transmission de la convention APL à la signature du préfet",
    )
    RETOUR_PREFET = (
        "RETOUR_PREFET",
        "Retour de la convention APL signée par le préfet",
    )
    ENVOI_HYPOTHEQUE = (
        "ENVOI_HYPOTHEQUE",
        "Transmission de la convention APL au bureau des hypothèques ou au"
        "livre foncier",
    )
    RETOUR_HYPOTHEQUE = (
        "RETOUR_HYPOTHEQUE",
        "Retour du bureau des hypothèques ou au livre foncier, pour modification",
    )
    ENVOI_RECTIFICATIF_PREFET = (
        "ENVOI_RECTIFICATIF_PREFET",
        "Transmission de l'attestation rectificative à la signature du préfet",
    )
    RETOUR_RECTIFICATIF_PREFET = (
        "RETOUR_RECTIFICATIF_PREFET",
        "Retour de l'attestation préfectorale de la convention APL",
    )
    PUBLICATION_HYPOTHEQUE = (
        "PUBLICATION_HYPOTHEQUE",
        "Publication de la convention APL au bureau des hypothèques",
    )
    ENVOI_CAF = "ENVOI_CAF", "Transmission de la convention APL à la CAF"
    DEPOT_AVENANT = "DEPOT_AVENANT", "Dépôt d'un avenant par le bailleur"
    INSTRUCTION_AVENANT = (
        "INSTRUCTION_AVENANT",
        "Instruction d'un avenant, objet de l'avenant, etc...",
    )
    CORRECTION_AVENANT = (
        "CORRECTION_AVENANT",
        "Modification de l'avenant sur demande de l'instructeur auprès du bailleur",
    )
    ENVOI_AVENANT_PREFET = (
        "ENVOI_AVENANT_PREFET",
        "Transmission de l'avenant à la signature du préfet",
    )
    SIGNATURE_AVENANT_PREFET = (
        "SIGNATURE_AVENANT_PREFET",
        "Retour de l'avenant signé par le préfet",
    )
    ENVOI_AVENANT_HYPOTHEQUE = (
        "ENVOI_AVENANT_HYPOTHEQUE",
        "Transmission de l'avenant au bureau des hypothèques ou au livre foncier",
    )
    RETOUR_AVENANT_HYPOTHEQUE = (
        "RETOUR_AVENANT_HYPOTHEQUE",
        "Retour de l'avenant du bureau des hypothèques ou du livre foncier,"
        "pour modification",
    )
    ENVOI_RECTIFICATIF_AVENANT_PREFET = (
        "ENVOI_RECTIFICATIF_AVENANT_PREFET",
        "Transmission de l'attestation rectificative d'avenant à la signature"
        "du préfet",
    )
    RETOUR_RECTIFICATIF_AVENANT_PREFET = (
        "RETOUR_RECTIFICATIF_AVENANT_PREFET",
        "Retour de l'attestation préfectorale de l'avenant",
    )
    PUBLICATION_AVENANT_HYPOTHEQUE = (
        "PUBLICATION_AVENANT_HYPOTHEQUE",
        "Publication de l'avenant de la convention APL au bureau des hypothèques",
    )
    EXPIRATION_CONVENTION = "EXPIRATION_CONVENTION", "Expiration de la convention APL"
    ENVOI_FIN_DENONCIATION = (
        "ENVOI_FIN_DENONCIATION",
        "Information auprès du bailleur de la date butoir de dénonciation de"
        "la convention APL",
    )
    AUTRE = "AUTRE", "Autres"
