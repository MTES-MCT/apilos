import functools
from datetime import date
from typing import Any

from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.urls import resolve

from apilos_settings.models import Departement
from conventions.models.convention import Convention
from programmes.models import IndiceEvolutionLoyer, NatureLogement
from programmes.models.models import Programme
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import (
    get_or_create_conventions,
    get_or_create_programme_from_siap_operation,
)


class OperationService:
    client: SIAPClient
    numero_operation: str
    requets: HttpRequest
    operation: dict[str, Any]
    programme: Programme
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

    def is_seconde_vie(self):
        for aide in self.operation["donneesOperation"]["aides"]:
            if aide["code"] == "SECD_VIE":
                return True
        return False

    def has_conventions(self):
        number_of_conventions = Convention.objects.filter(
            programme_id=self.programme.id
        ).count()
        return number_of_conventions == len(self.operation["detailsOperation"])

    def get_or_create_programme(self):
        if self.siap_error:
            raise self.siap_exception_detail
        self.programme = get_or_create_programme_from_siap_operation(self.operation)
        return self.programme

    def get_or_create_conventions(self):
        if self.siap_error:
            # impossible to get operation from SIAP
            return (None, None, None)
        return get_or_create_conventions(self.operation, self.request.user)

    def get_context_list_conventions(self, paginator) -> dict:
        return {
            "url_name": resolve(self.request.path_info).url_name,
            "order_by": self.request.GET.get("order_by", ""),
            "numero_operation": self.numero_operation,
            "programme": self.programme,
            "conventions": paginator.get_page(self.request.GET.get("page", 1)),
            "filtered_conventions_count": paginator.count,
            "all_conventions_count": paginator.count,
            "siap_assistance_url": settings.SIAP_ASSISTANCE_URL,
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
