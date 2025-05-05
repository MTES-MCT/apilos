from typing import Any

TIMEOUT_MESSAGE = (
    "Le module conventionnement ne parvient pas à joindre la plateforme SIAP,"
    " merci de réessayer plus tard"
)

HABILITATION_MESSAGE = (
    "La plateforme SIAP n'a pas pu trouver d'habilitation associée" " à votre profil"
)

FUSION_MESSAGE = (
    "La plateforme SIAP a retourné une erreur lors de la récupération des bailleurs"
    " fusionnés"
)

UNAUTHORIZED_MESSAGE = (
    "La plateforme SIAP indique que vous n'êtes pas authorisé à accéder à cette"
    " ressource"
)

NOT_FOUND_MESSAGE = "La plateforme SIAP n'a pas pu trouver la ressource demandée"

CONVENTION_NOT_NEEDED_MESSAGE = (
    "Aucune aide ne nécessite un conventionnement pour cette opération"
)
NOT_COMPLETED_MESSAGE = (
    "Les informations fournies par la plateforme SIAP ne sont pas suffisantes"
    " pour permettre le conventionnement"
)

BAILLEUR_IDENTIFICATION_MESSAGE = (
    "Impossible d'identifier le bailleur selon les"
    " informations transmises par la plateforme SIAP"
)


class SIAPException(Exception):  # noqa: N818
    pass


class DuplicatedOperationSIAPException(SIAPException):
    numero_operation: str

    def __init__(self, numero_operation: str):
        self.numero_operation = numero_operation
        super().__init__(f"L'opération {numero_operation} est en doublon")


class ConflictedOperationSIAPException(SIAPException):
    numero_operation: str
    diff: dict[str, Any] = None

    def __init__(self, numero_operation: str, diff: dict[str, Any]):
        self.numero_operation = numero_operation
        self.diff = diff
        super().__init__(f"L'opération {numero_operation} est en doublon")
