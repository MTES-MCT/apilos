import datetime
from dataclasses import dataclass

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest

from conventions.forms.convention_from_operation import (
    AddAvenantForm,
    AddConventionForm,
)
from conventions.models import Convention, ConventionStatut
from conventions.models.avenant_type import AvenantType
from conventions.services.file import ConventionFileService
from conventions.services.utils import ReturnStatus
from programmes.models import NatureLogement, Programme
from programmes.models.choices import FinancementEDD
from programmes.models.models import Lot
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import get_or_create_programme_from_siap_operation


@dataclass
class Operation:
    numero: str
    nom: str
    bailleur: str
    nature: str
    commune: str

    siap_payload: dict[str, str] | None = None

    @classmethod
    def from_siap_payload(cls, payload: dict[str, str]) -> "Operation":
        return cls(
            nom=payload["donneesOperation"]["nomOperation"],
            numero=payload["donneesOperation"]["numeroOperation"],
            nature=payload["donneesOperation"]["natureLogement"],
            bailleur=payload["donneesMo"]["nom"],
            commune=payload["donneesLocalisation"]["adresseComplete"]["commune"],
            siap_payload=payload,
        )

    @classmethod
    def from_apilos_programme(cls, programme: Programme) -> "Operation":
        return cls(
            numero=programme.numero_operation,
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
        qs = self._user_programmes().filter(
            numero_operation=self.numero_operation, parent_id=None
        )
        if qs.count() == 1:
            return Operation.from_apilos_programme(programme=qs.first())
        return None

    def _get_nearby_apilos_operations(self) -> list[Operation]:
        qs = (
            self._user_programmes()
            .annotate(
                numero_operation_trgrm=TrigramSimilarity(
                    "numero_operation_pour_recherche",
                    self.numero_operation.replace("-", "")
                    .replace("/", "")
                    .replace(".", "")
                    .replace(" ", ""),
                )
            )
            .filter(
                numero_operation_trgrm__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                parent_id=None,
            )
            .order_by("-numero_operation_trgrm", "-cree_le")
        )
        return [Operation.from_apilos_programme(programme=p) for p in qs[:10]]


class AddConventionService:
    request: HttpRequest
    form: AddConventionForm
    operation: Operation | None = None
    convention: Convention | None = None
    conventions: list[Convention]

    def __init__(self, request: HttpRequest, operation: Operation | None) -> None:
        self.request = request
        self.operation = operation
        self.conventions = self._get_conventions(operation=self.operation)
        financements = self._get_financements(conventions=self.conventions)

        if request.method == "POST":
            self.form = AddConventionForm(
                request.POST, request.FILES, financements=financements
            )
        else:
            self.form = AddConventionForm(financements=financements)

    def _get_conventions(self, operation: Operation | None) -> QuerySet[Convention]:
        if operation is None:
            return Convention.objects.none()

        programme = (
            Programme.objects.filter(
                numero_operation=self.operation.numero, parent_id=None
            )
            .order_by("-cree_le")
            .first()
        )
        if programme is None:
            return Convention.objects.none()

        return Convention.objects.filter(programme_id=programme.id)

    def _get_financements(
        self, conventions: QuerySet[Convention]
    ) -> list[tuple[str, str]]:
        existing_financements = Lot.objects.filter(
            convention_id__in=conventions.values_list("id", flat=True)
        ).values_list("financement", flat=True)
        return [
            financement
            for financement in FinancementEDD.choices
            if financement[0] not in existing_financements
        ]

    def _create_convention(self, programme: Programme) -> Convention:
        convention = Convention.objects.create(
            programme=programme,
            cree_par=self.request.user,
            numero=self.form.cleaned_data["numero"],
            televersement_convention_signee_le=datetime.date(
                int(self.form.cleaned_data["annee_signature"]), 1, 1
            ),
            statut=ConventionStatut.SIGNEE.label,
        )

        return convention

    def _create_lot(self, convention: Convention) -> Lot:
        return Lot.objects.create(
            convention=convention,
            financement=self.form.cleaned_data["financement"],
            nb_logements=self.form.cleaned_data["nb_logements"],
        )

    def save(self) -> ReturnStatus:
        if not self.form.is_valid():
            return ReturnStatus.ERROR

        with transaction.atomic():
            try:
                if self.operation.siap_payload:
                    programme = get_or_create_programme_from_siap_operation(
                        self.operation.siap_payload
                    )
                else:
                    programme = Programme.objects.get(
                        numero_operation=self.operation.numero, parent_id=None
                    )

                self.convention = self._create_convention(programme=programme)
                self._create_lot(convention=self.convention)

                file = self.request.FILES.get("nom_fichier_signe", False)
                if file:
                    ConventionFileService.upload_convention_file(
                        self.convention, file, update_statut=False
                    )

                return ReturnStatus.SUCCESS

            except IntegrityError as err:
                # TODO: handle this error correctly
                self.form.add_error(field=None, error=str(err))
                return ReturnStatus.ERROR


class AddAvenantsService:
    request: HttpRequest
    convention: Convention
    form: AddAvenantForm

    def __init__(self, request: HttpRequest, convention: Convention) -> None:
        self.request = request
        self.convention = convention

        bailleur_query = request.user.bailleur_query_set(
            only_bailleur_uuid=self.convention.programme.bailleur.uuid,
        )

        if request.method == "POST":
            self.form = AddAvenantForm(
                data=request.POST,
                files=request.FILES,
                bailleur_query=bailleur_query,
            )
        else:
            self.form = AddAvenantForm(
                bailleur_query=bailleur_query,
                initial={
                    "bailleur": self.convention.programme.bailleur,
                    "nb_logements": self.convention.lot.nb_logements,
                },
            )

    def save(self) -> ReturnStatus:
        if not self.form.is_valid():
            return ReturnStatus.ERROR

        with transaction.atomic():
            try:
                avenant = self.convention.clone(
                    self.request.user, convention_origin=self.convention
                )

                avenant.numero = self.form.cleaned_data["numero"]
                avenant.statut = ConventionStatut.SIGNEE.label
                avenant.televersement_convention_signee_le = datetime.date(
                    int(self.form.cleaned_data["annee_signature"]), 1, 1
                )
                avenant.save()

                file = self.request.FILES.get("nom_fichier_signe", False)
                if file:
                    ConventionFileService.upload_convention_file(
                        convention=avenant, file=file, update_statut=False
                    )

                # Avenant type Champ libre
                if champ_libre_avenant := self.form.cleaned_data["champ_libre_avenant"]:
                    avenant.champ_libre_avenant = champ_libre_avenant
                    avenant.save()
                    avenant.avenant_types.add(
                        AvenantType.objects.get(nom="champ_libre")
                    )

                # Avenant type Bailleur
                bailleur = self.form.cleaned_data["bailleur"]
                if bailleur and bailleur != self.convention.programme.bailleur:
                    self.convention.programme.bailleur = bailleur
                    self.convention.programme.save()
                    avenant.avenant_types.add(AvenantType.objects.get(nom="bailleur"))

                # Avenant type Logements
                nb_logements = self.form.cleaned_data["nb_logements"]
                if nb_logements and nb_logements != self.convention.lot.nb_logements:
                    lot_convention = self.convention.lot
                    lot_convention.nb_logements = nb_logements
                    lot_convention.save()
                    avenant.avenant_types.add(AvenantType.objects.get(nom="logements"))

                return ReturnStatus.SUCCESS

            except IntegrityError as err:
                # TODO: handle this error correctly
                self.form.add_error(field=None, error=str(err))
                return ReturnStatus.ERROR
