from dataclasses import dataclass

from django.http import HttpRequest

from conventions.forms.convention_form_add import ConventionAddForm
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient


@dataclass
class Operation:
    numero: str
    nom: str
    bailleur: str
    nature: str
    commune: str


class SelectOperationService:
    request: HttpRequest
    numero_operation: str

    def __init__(self, request: HttpRequest, numero_operation: str) -> None:
        self.request = request
        self.numero_operation = numero_operation

    def fetch_operations(self) -> tuple[bool, list[Operation]]:
        if self.numero_operation is None:
            return False, []

        if operation := self._fetch_siap_operation():
            return True, [operation]

        # TODO: fetch operations from Apilos database
        return False, []

    def _fetch_siap_operation(self) -> Operation | None:
        try:
            payload = SIAPClient.get_instance().get_operation(
                user_login=self.request.user.cerbere_login,
                habilitation_id=self.request.session["habilitation_id"],
                operation_identifier=self.numero_operation,
            )
        except SIAPException:
            return None

        return Operation(
            nom=payload["donneesOperation"]["nomOperation"],
            numero=payload["donneesOperation"]["numeroOperation"],
            nature=payload["donneesOperation"]["natureLogement"],
            bailleur=payload["gestionnaire"]["code"],
            commune=payload["donneesLocalisation"]["adresseComplete"]["commune"],
        )


class ConventionAddService:
    request: HttpRequest
    form: ConventionAddForm

    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.form = None

    def get_form(self) -> ConventionAddForm:
        if self.form is None:
            self.form = ConventionAddForm()
        return self.form
