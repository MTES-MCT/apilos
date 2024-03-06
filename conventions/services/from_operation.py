import datetime
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db import IntegrityError, transaction
from django.db.models import QuerySet, Value
from django.db.models.functions import Replace
from django.forms import formset_factory
from django.http import HttpRequest

from conventions.forms.convention_from_operation import (
    AddAvenantForm,
    AddAvenantFormSet,
    AddConventionForm,
)
from conventions.models import Convention, ConventionStatut
from conventions.models.avenant_type import AvenantType
from conventions.services import utils
from conventions.services.file import ConventionFileService
from programmes.models import NatureLogement, Programme
from programmes.models.models import Lot
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import (
    get_or_create_programme_from_siap_operation,
)


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
            # FIXME: use entiteMorale.nom
            bailleur=payload["gestionnaire"]["code"],
            commune=payload["donneesLocalisation"]["adresseComplete"]["commune"],
            siap_payload=payload,
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


class AddConventionService:
    request: HttpRequest
    form: AddConventionForm
    return_status: utils.ReturnStatus
    operation: Operation
    convention: Convention | None = None

    def __init__(self, request: HttpRequest, operation: Operation) -> None:
        self.request = request
        self.operation = operation

        # TODO: exclure des choix de financement du formulaire, si une convention existe déjà pour ce programme
        if request.method == "POST":
            self.form = AddConventionForm(request.POST, request.FILES)
        else:
            self.form = AddConventionForm()

    def _create_lot(self, programme: Programme) -> Lot:
        return Lot.objects.create(
            programme=programme,
            financement=self.form.cleaned_data["financement"],
            nb_logements=self.form.cleaned_data["nb_logements"],
        )

    def _create_convention(self, lot: Lot) -> Convention:
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

    def save(self) -> None:
        if not self.form.is_valid():
            self.return_status = utils.ReturnStatus.ERROR
            return

        with transaction.atomic():
            try:
                if self.operation.siap_payload:
                    programme = get_or_create_programme_from_siap_operation(
                        self.operation.siap_payload
                    )
                else:
                    programme = Programme.objects.get(
                        numero_galion=self.operation.numero
                    )

                lot = self._create_lot(programme=programme)
                self.convention = self._create_convention(lot=lot)

                file = self.request.FILES.get("nom_fichier_signe", False)
                if file:
                    ConventionFileService.upload_convention_file(self.convention, file)

            except IntegrityError as err:
                # TODO: handle this error correctly
                self.form.add_error(field=None, error=str(err))
                self.return_status = utils.ReturnStatus.ERROR
                return

        self.return_status = utils.ReturnStatus.SUCCESS


AddAvenantFormSetFactory = formset_factory(
    form=AddAvenantForm, formset=AddAvenantFormSet
)


class AddAvenantsService:
    request: HttpRequest
    convention: Convention
    formset: AddAvenantFormSet

    def __init__(self, request: HttpRequest, convention: Convention) -> None:
        self.request = request
        self.convention = convention

        if request.method == "POST":
            self.formset = AddAvenantFormSetFactory(
                initial=self._get_form_initial(), data=request.POST, files=request.FILES
            )
        else:
            self.formset = AddAvenantFormSetFactory(initial=self._get_form_initial())

    def _get_form_initial(self) -> list[dict[str, Any]]:
        return [
            {
                "uuid": avenant.uuid,
                "numero": avenant.numero,
                "avenant_type": avenant.avenant_types.first().nom,
                # FIXME
                # "annee_signature": avenant.televersement_convention_signee_le.year,
                "annee_signature": 0,
                "nom_fichier_signe": avenant.nom_fichier_signe,
            }
            for avenant in self.convention.avenants.all()
        ]

    def save(self) -> None:
        if not self.formset.is_valid():
            return

        for form in self.formset:
            if form.cleaned_data["uuid"]:
                continue

            with transaction.atomic():
                try:
                    avenant = self.convention.clone(
                        self.request.user, convention_origin=self.convention
                    )

                    file = self.request.FILES.get("nom_fichier_signe", False)
                    if file:
                        ConventionFileService.upload_convention_file(
                            convention=avenant, file=file, update_statut=False
                        )

                    avenant.numero = form.cleaned_data["numero"]
                    avenant.statut = ConventionStatut.SIGNEE.label
                    # FIXME
                    # avenant.televersement_convention_signee_le = (
                    #     datetime.date(form.cleaned_data["annee_signature"], 1, 1),
                    # )
                    avenant.save()

                    avenant_type = AvenantType.objects.get(
                        nom=form.cleaned_data["avenant_type"]
                    )
                    avenant.avenant_types.add(avenant_type)

                except IntegrityError as err:
                    # TODO: handle this error correctly
                    self.form.add_error(field=None, error=str(err))
