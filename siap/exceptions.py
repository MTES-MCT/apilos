from typing import Any


class SIAPException(Exception):
    pass


class HabilitationSIAPException(SIAPException):
    pass


class TimeoutSIAPException(SIAPException):
    pass


class AssociationHLMSIAPException(SIAPException):
    pass


class UnauthorizedSIAPException(SIAPException):
    pass


class UnavailableServiceSIAPException(SIAPException):
    pass


class NoConventionForOperationSIAPException(SIAPException):
    pass


class InconsistentDataSIAPException(SIAPException):
    pass


class NotHandledBailleurPriveSIAPException(SIAPException):
    pass


class FusionAPISIAPException(SIAPException):
    pass


class DuplicatedOperationSIAPException(SIAPException):
    numero_operation: str

    def __init__(self, numero_operation: str):
        self.numero_operation = numero_operation
        super().__init__(f"L'opération {numero_operation} est en doublon")


class OperationToRepairSIAPException(DuplicatedOperationSIAPException):
    diff: dict[str, Any] = None

    def __init__(self, numero_operation: str, diff: dict[str, Any]):
        super().__init__(numero_operation)
        self.diff = diff
