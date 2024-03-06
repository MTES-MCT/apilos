import datetime
from dataclasses import dataclass

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db import transaction
from django.db.models import QuerySet, Value
from django.db.models.functions import Replace
from django.http import HttpRequest

from conventions.forms.convention_form_add import ConventionAddForm
from conventions.models.convention import Convention
from conventions.services import utils
from conventions.services.file import ConventionFileService
from conventions.services.selection import _get_choices_from_object
from conventions.templatetags.custom_filters import is_instructeur
from instructeurs.models import Administration
from programmes.models import NatureLogement, Programme
from programmes.models.models import Lot
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import (
    get_or_create_programme_from_siap,
)


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

    def get_operation(self) -> Operation | None:
        return self._fetch_siap_operation() or self._get_apilos_operation()

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
            self.form = ConventionAddForm(
                self.request.POST,
                self.request.FILES,
            )
        return self.form

    def _get_bailleur_query(self, uuid: str | None = None):
        queryset = self.request.user.bailleurs(full_scope=True)
        if uuid:
            return queryset.all()

        return queryset[0 : settings.APILOS_MAX_DROPDOWN_COUNT]

    def _get_administration_choices(self):
        return _get_choices_from_object(
            self.request.user.administrations()
            if is_instructeur(self.request)
            else Administration.objects.all().order_by("nom")
        )

    def _create_lot(self, programme):
        lot = Lot.objects.create(
            nb_logements=self.form.cleaned_data["nb_logements"],
            financement=self.form.cleaned_data["financement"],
            programme=programme,
        )
        return lot

    def _create_convention(self, lot):
        return Convention.objects.create(
            lot=lot,
            programme_id=lot.programme_id,
            financement=lot.financement,
            cree_par=self.request.user,
            numero=self.form.cleaned_data["numero"],
            televersement_convention_signee_le=datetime.date(
                self.form.cleaned_data["annee_signature"], 1, 1
            ),
        )

    def post_create_convention(self, numero_operation):
        try:
            operation_siap = SIAPClient.get_instance().get_operation(
                user_login=self.request.user.cerbere_login,
                habilitation_id=self.request.session["habilitation_id"],
                operation_identifier=numero_operation,
            )
        except SIAPException:
            operation_siap = None

        form = self.get_form()
        if form.is_valid():
            with transaction.atomic():
                programme = get_or_create_programme_from_siap(operation_siap)
                lot = self._create_lot(programme=programme)
                self.convention = self._create_convention(lot=lot)

                file = self.request.FILES.get("nom_fichier_signe", False)
                if file:
                    ConventionFileService.upload_convention_file(self.convention, file)
            self.return_status = utils.ReturnStatus.SUCCESS
        else:
            self.return_status = utils.ReturnStatus.ERROR
