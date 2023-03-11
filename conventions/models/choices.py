from django.db.models import TextChoices


class ConventionStatut(TextChoices):
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

    PROJET = "1. Projet", "Projet"

    INSTRUCTION = (
        "2. Instruction requise",
        "En instruction",
    )
    CORRECTION = (
        "3. Corrections requises",
        "En correction",
    )
    A_SIGNER = "4. A signer", "À signer"
    SIGNEE = "5. Signée", "Finalisée"
    RESILIEE = "6. Résiliée", "Résiliée"
    DENONCEE = "7. Dénoncée", "Dénoncée"
    ANNULEE = "8. Annulée en suivi", "Annulée en suivi"

    @classmethod
    def active_statuts(cls):
        return [cls.PROJET, cls.INSTRUCTION, cls.CORRECTION, cls.A_SIGNER]

    @classmethod
    def completed_statuts(cls):
        return [cls.SIGNEE, cls.RESILIEE, cls.DENONCEE, cls.ANNULEE]


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
