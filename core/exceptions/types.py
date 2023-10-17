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
