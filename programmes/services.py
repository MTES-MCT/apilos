import functools
from datetime import date
from typing import Any

from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.urls import resolve

from apilos_settings.models import Departement
from conventions.models.choices import ConventionStatut
from conventions.models.convention import Convention
from programmes.models import IndiceEvolutionLoyer, NatureLogement
from programmes.models.choices import TypeOperation
from programmes.models.models import Programme
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import (
    get_filtered_aides,
    get_or_create_conventions_from_siap,
    get_or_create_lots_and_conventions_by_financement,
    get_or_create_programme_from_siap_operation,
)


class OperationService:
    client: SIAPClient
    numero_operation: str
    requets: HttpRequest
    operation: dict[str, Any] | None = None
    programmes: list[Programme]  # queryset of programmes
    siap_error: bool = False
    siap_exception_detail: SIAPException

    def __init__(self, request: HttpRequest, numero_operation: str) -> None:
        self.request = request
        self.client = SIAPClient.get_instance()
        self.numero_operation = numero_operation

        try:
            self.operation = self.client.get_operation(
                user_login=request.user.cerbere_login,
                habilitation_id=request.session["habilitation_id"],
                operation_identifier=numero_operation,
            )
        except SIAPException as e:
            self.siap_error = True
            self.siap_exception_detail = e

    def get_or_create_operation(self) -> list[Programme]:
        """
        Récupère les opérations existantes et crée une opération si aucune existe
        """
        self.programmes = list(
            Programme.objects.filter(numero_operation=self.numero_operation)
        )
        if len(self.programmes) == 0:
            programme = get_or_create_programme_from_siap_operation(self.operation)
            self.programmes = [programme]
        return self.programmes

    def programme(self):
        return self.programmes[0] if len(self.programmes) > 0 else None

    def check_sans_financement_consistancy(self):
        if len(self.programmes) > 1:
            if self.operation["donneesOperation"]["sansTravaux"] and any(
                programme.type_operation != TypeOperation.SANSTRAVAUX
                for programme in self.programmes
            ):
                # TODO : return a issue instead of raise?
                raise ValueError(
                    "Multi programme avec certain en sans financement et d'autre avec financements"
                )

    def is_seconde_vie(self):
        if self.operation is None:
            return False
        for aide in self.operation["donneesOperation"]["aides"]:
            if aide["code"] == "SECD_VIE":
                return True
        return False

    def get_active_conventions(self) -> QuerySet[Convention]:
        return (
            Convention.objects.filter(
                programme__numero_operation=self.numero_operation, parent__isnull=True
            )
            .exclude(statut=ConventionStatut.ANNULEE.label)
            .distinct()
        )

    def has_conventions(self):
        number_of_conventions = self.get_active_conventions().count()
        return number_of_conventions == len(self.operation["detailsOperation"])

    def get_or_create_programme(self):
        if self.siap_error:
            raise self.siap_exception_detail
        self.programme = get_or_create_programme_from_siap_operation(self.operation)
        return self.programme

    def collect_conventions_by_financements(self):
        conventions = self.get_active_conventions().prefetch_related("lots")
        if self.operation is None:
            # group by financement
            conventions_by_financements = {}
            for convention in conventions:
                for financement in convention.lots.all():
                    if financement not in conventions_by_financements:
                        conventions_by_financements[financement] = []
                    conventions_by_financements[financement].append(convention)
        else:
            filtered_op_aides = get_filtered_aides(self.operation)
            conventions_by_financements = {}
            for aide in filtered_op_aides:
                conventions_by_financements[aide] = [
                    convention
                    for convention in conventions
                    for lot in convention.lots.all()
                    if lot.financement == aide
                ]
        return conventions_by_financements

    def create_convention_by_financement(self, programme, financement):
        get_or_create_lots_and_conventions_by_financement(
            self.operation, programme, self.request.user, financement
        )

    def get_or_create_conventions(self):
        if self.siap_error:
            # impossible to get operation from SIAP
            return (None, None, None)
        return get_or_create_conventions_from_siap(self.operation, self.request.user)

    def get_context_list_conventions(self, paginator) -> dict:
        return {
            "url_name": resolve(self.request.path_info).url_name,
            "order_by": self.request.GET.get("order_by", ""),
            "numero_operation": self.numero_operation,
            "programme": self.programme,
            "conventions": paginator.get_page(self.request.GET.get("page", 1)),
            "filtered_conventions_count": paginator.count,
            "all_conventions_count": paginator.count,
            "search_operation_nom": "",
            "search_numero": "",
            "search_lieu": "",
        }


def _find_index_by_annee(annee: str, evolutions: list[dict[str, Any]]) -> int:
    for i, dic in enumerate(evolutions):
        if dic["annee"] == annee:
            return i
    return -1


class LoyerRedevanceUpdateComputer:
    @staticmethod
    def compute_loyer_update(
        montant_initial: float,
        nature_logement: str,
        date_initiale: date,
        departement: Departement,
        date_actualisation: date | None = None,
    ) -> float:
        if date_actualisation is None:
            date_actualisation = date.today()

        if nature_logement not in NatureLogement.eligible_for_update():
            raise Exception(f"Nature de logement invalide {nature_logement}")

        qs = (
            IndiceEvolutionLoyer.objects.filter(
                nature_logement=(
                    nature_logement
                    if nature_logement != NatureLogement.LOGEMENTSORDINAIRES
                    else None
                ),
                is_loyer=nature_logement == NatureLogement.LOGEMENTSORDINAIRES,
            )
            .filter(
                # Soit la plage de dates "englobe" la période
                Q(date_debut__gt=date_initiale, date_fin__lt=date_actualisation)
                |
                # Soit la date initiale est située sur la période
                Q(date_debut__lte=date_initiale, date_fin__gte=date_initiale)
            )
            .order_by("date_debut")
        )

        evolutions_departements = list(
            qs.filter(departements__id=departement.id).values("annee", "evolution")
        )
        evolutions = list(qs.filter(departements__id=None).values("annee", "evolution"))

        for indice in evolutions_departements:
            i = _find_index_by_annee(indice["annee"], evolutions)
            if i >= 0:
                evolutions[i]["evolution"] = indice["evolution"]

        return functools.reduce(
            lambda loyer, evolution: loyer * ((100.0 + evolution["evolution"]) / 100.0),
            evolutions,
            montant_initial,
        )
