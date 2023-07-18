from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import QuerySet

from bailleurs.models import Bailleur
from conventions.models import Convention, ConventionStatut
from instructeurs.models import Administration
from programmes.models import Programme
from users.models import User


class ConventionSearchBaseService(ABC):
    order_by = None
    prefetch = []
    filters = defaultdict()

    @abstractmethod
    def _get_base_queryset(self) -> QuerySet:
        pass

    def _get_order_by(self) -> List:
        if not isinstance(self.order_by, list):
            self.order_by = [self.order_by]

        return [field_to_order for field_to_order in self.order_by if field_to_order]

    def get_count_for(self, tab):
        filters = {**self.filters, "statut__in": [statut.label for statut in tab]}
        return self._get_base_queryset().filter(**filters).count()

    def get_queryset(self) -> QuerySet:
        queryset = self._get_base_queryset()

        if self.filters:
            queryset = queryset.filter(**self.filters)

        if self.prefetch:
            queryset = queryset.prefetch_related(*self.prefetch)

        if order_by := self._get_order_by():
            queryset = queryset.order_by(*order_by)

        return queryset

    def paginate(self, size: int | None = None) -> Paginator:
        return Paginator(
            self.get_queryset(), size or settings.APILOS_PAGINATION_PER_PAGE
        )


class AvenantListSearchService(ConventionSearchBaseService):
    prefetch = ["programme", "lot"]

    def __init__(self, convention: Convention, order_by_numero: bool = False):
        self.convention: Convention = (
            convention.parent if convention.is_avenant() else convention
        )

        if order_by_numero:
            self.order_by = "numero"

    def _get_base_queryset(self) -> QuerySet:
        return self.convention.avenants.all()


class ProgrammeConventionSearchService(ConventionSearchBaseService):
    prefetch = ["programme", "programme__administration", "lot"]

    def __init__(self, programme: Programme, order_by: str | None = None):
        self.programme: Programme = programme

        if order_by:
            self.order_by = order_by

    def _get_base_queryset(self) -> QuerySet:
        return Convention.objects.filter(programme=self.programme)


class UserConventionSearchService(ConventionSearchBaseService):
    def __init__(
        self,
        user: User,
        statuses: List[ConventionStatut] = None,
        order_by: str | None = None,
        statut: str | None = None,
        financement: str | None = None,
        departement: str | None = None,
        commune: str | None = None,
        search_input: str | None = None,
        anru: bool = False,
        bailleur: Bailleur | None = None,
        administration: Administration | None = None,
    ):
        self.user: User = user
        self.order_by: str | None = order_by
        self.statuses = statuses or []
        self.statut: ConventionStatut | None = (
            ConventionStatut.get_by_label(statut) if statut else None
        )
        self.financement: str | None = financement
        self.departement: str | None = departement
        self.commune: str | None = commune
        self.search_input: str | None = search_input
        self.anru: bool = anru
        self.bailleur: Bailleur | None = bailleur
        self.administration: Administration | None = administration

    def _build_filters(self):
        filters = defaultdict()

        if self.statuses:
            filters["statut__in"] = map(lambda s: s.label, self.statuses)

        if self.statut:
            filters["statut"] = self.statut.label

        if self.commune:
            filters["programme__ville__icontains"] = self.commune

        if self.financement:
            filters["financement"] = self.financement

        self.filters = filters

    def _get_base_queryset(self) -> QuerySet:
        self._build_filters()
        return (
            self.user.conventions()
            .prefetch_related("programme")
            .prefetch_related("programme__administration")
            .prefetch_related("lot")
        )
