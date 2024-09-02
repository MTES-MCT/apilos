from typing import Any


class SIAPException(Exception):  # noqa: N818
    pass


class HabilitationSIAPException(SIAPException):
    pass


class TimeoutSIAPException(SIAPException):
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


class ConflictedOperationSIAPException(SIAPException):
    numero_operation: str
    diff: dict[str, Any] = None

    def __init__(self, numero_operation: str, diff: dict[str, Any]):
        self.numero_operation = numero_operation
        self.diff = diff
        super().__init__(f"L'opération {numero_operation} est en doublon")
