from enum import Enum
from typing import NamedTuple
from django.db.models import TextChoices


class StatutByRole(NamedTuple):
    label: str
    icon_html_class: str | None = None
    call_to_action: str | None = None


class ConventionStatut(Enum):
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
        bailleurs: StatutByRole
        instructeurs: StatutByRole

    PROJET = Definition("1. Projet", StatutByRole("Projet"), StatutByRole("Projet"))

    INSTRUCTION = Definition(
        "2. Instruction requise",
        StatutByRole("En cours d'instruction"),
        StatutByRole("À instruire"),
    )
    CORRECTION = Definition(
        "3. Corrections requises",
        StatutByRole("À corriger"),
        StatutByRole("Encopurs de correction"),
    )
    A_SIGNER = Definition(
        "4. A signer", StatutByRole("À signer"), StatutByRole("À signer")
    )
    SIGNEE = Definition(
        "5. Signée", StatutByRole("Finalisée"), StatutByRole("Finalisée")
    )
    RESILIEE = Definition(
        "6. Résiliée", StatutByRole("Résiliée"), StatutByRole("Résiliée")
    )
    DENONCEE = Definition(
        "7. Dénoncée", StatutByRole("Dénoncée"), StatutByRole("Dénoncée")
    )
    ANNULEE = Definition(
        "8. Annulée en suivi",
        StatutByRole("Annulée en suivi"),
        StatutByRole("Annulée en suivi"),
    )

    # @classmethod
    # @property
    # def choices(cls) -> list[tuple[str, str]]:
    #     return [(member.name, member.label) for member in cls]
    @classmethod
    @property
    def choices(cls) -> list[tuple[str, str]]:
        return [(member.name, member.label) for member in cls]

    @classmethod
    def active_statuts(cls):
        return [
            c.label for c in [cls.PROJET, cls.INSTRUCTION, cls.CORRECTION, cls.A_SIGNER]
        ]

    @classmethod
    def completed_statuts(cls):
        return [c.label for c in [cls.SIGNEE, cls.RESILIEE, cls.DENONCEE, cls.ANNULEE]]

    @property
    def label(self):
        return self.value.label

    @property
    def bailleur_label(self):
        return self.value.bailleur.label

    @property
    def instructeur_label(self):
        return self.value.instructeur.label


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
    AUTRE = "AUTRE", "Autre"
