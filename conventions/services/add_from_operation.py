from dataclasses import dataclass

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import QuerySet, Value
from django.db.models.functions import Replace
from django.http import HttpRequest

from conventions.forms.convention_form_add import ConventionAddForm
from programmes.models import NatureLogement, Programme
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient


@dataclass
class Operation:
    numero: str
    nom: str
    bailleur: str
    nature: str
    commune: str

    @classmethod
    def from_siap_payload(cls, payload: dict[str, str]) -> "Operation":
        return cls(
            nom=payload["donneesOperation"]["nomOperation"],
            numero=payload["donneesOperation"]["numeroOperation"],
            nature=payload["donneesOperation"]["natureLogement"],
            bailleur=payload["gestionnaire"]["code"],
            commune=payload["donneesLocalisation"]["adresseComplete"]["commune"],
        )

    @classmethod
    def from_apilos_programme(cls, programme: Programme) -> "Operation":
        return cls(
            numero=programme.numero_galion,
            nom=programme.nom,
            bailleur=programme.bailleur.nom,
            nature=NatureLogement[programme.nature_logement].label,
            commune=programme.ville,
        )


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

        if operation := self._get_apilos_operation():
            return True, [operation]

        return False, self._get_nearby_apilos_operations()

    def _fetch_siap_operation(self) -> Operation | None:
        try:
            return Operation.from_siap_payload(
                payload=SIAPClient.get_instance().get_operation(
                    user_login=self.request.user.cerbere_login,
                    habilitation_id=self.request.session["habilitation_id"],
                    operation_identifier=self.numero_operation,
                )
            )
        except SIAPException:
            return None

    def _user_programmes(self) -> QuerySet[Programme]:
        return self.request.user.programmes()

    def _get_apilos_operation(self) -> Operation | None:
        qs = self._user_programmes().filter(numero_galion=self.numero_operation)
        if qs.count() == 1:
            return Operation.from_apilos_programme(programme=qs.first())
        return None

    def _get_nearby_apilos_operations(self) -> list[Operation]:
        qs = (
            self._user_programmes()
            .annotate(
                numero_operation_trgrm=TrigramSimilarity(
                    Replace(Replace("numero_galion", Value("/")), Value("-")),
                    self.numero_operation.replace("-", "").replace("/", ""),
                )
            )
            .filter(numero_operation_trgrm__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            .order_by("-numero_operation_trgrm", "-cree_le")
        )
        return [Operation.from_apilos_programme(programme=p) for p in qs[:10]]


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
