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
    filters = defaultdict()

    @abstractmethod
    def get_base_queryset(self) -> QuerySet:
        pass

    def get_order_by_fields(self) -> List:
        if not self.order_by:
            return ["cree_le"]
        return [self.order_by]

    def get_count_for_tab(self, tab):
        filters = {**self.filters, "statut__in": [statut.label for statut in tab]}
        return self.get_base_queryset().filter(**filters).count()

    def get_queryset(self) -> QuerySet:
        return (
            self.get_base_queryset()
            .filter(**self.filters)
            .order_by(*self.get_order_by_fields())
        )

    def paginate(self, size: int | None = None) -> Paginator:
        return Paginator(
            self.get_queryset(), size or settings.APILOS_PAGINATION_PER_PAGE
        )


class AvenantListSearchService(ConventionSearchBaseService):
    def __init__(self, convention: Convention, order_by_numero: bool = False):
        self.convention: Convention = (
            convention.parent if convention.is_avenant() else convention
        )
        self.order_by_numero: bool = order_by_numero

    def get_order_by_fields(self) -> List:
        return ["numero"] if self.order_by_numero else super().get_order_by_fields()

    def get_base_queryset(self) -> QuerySet:
        return (
            self.convention.avenants.all()
            .prefetch_related("programme")
            .prefetch_related("lot")
        )


class ProgrammeConventionSearchService(ConventionSearchBaseService):
    def __init__(self, programme: Programme, order_by: str | None = None):
        self.programme: Programme = programme
        self.order_by: str | None = order_by

    def get_base_queryset(self) -> QuerySet:
        return (
            Convention.objects.filter(programme=self.programme)
            .prefetch_related("programme")
            .prefetch_related("programme__administration")
            .prefetch_related("lot")
        )

    def get_order_by_fields(self) -> List:
        return [self.order_by] if self.order_by is not None else []


class UserConventionSearchService(ConventionSearchBaseService):
    def __init__(
        self,
        user: User,
        statuses: List[ConventionStatut],
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
        self.statuses = statuses
        self.statut: ConventionStatut | None = ConventionStatut.get_by_label(statut)
        self.financement: str | None = financement
        self.departement: str | None = departement
        self.commune: str | None = commune
        self.search_input: str | None = search_input
        self.anru: bool = anru
        self.bailleur: Bailleur | None = bailleur
        self.administration: Administration | None = administration

    def get_base_queryset(self) -> QuerySet:
        self.filters["statut__in"] = map(lambda s: s.label, self.statuses)

        if self.statut:
            self.filters["statut"] = self.statut.label

        if self.commune:
            self.filters["programme__ville__icontains"] = self.commune

        if self.financement:
            self.filters["financement"] = self.financement

        return (
            self.user.conventions()
            .prefetch_related("programme")
            .prefetch_related("programme__administration")
            .prefetch_related("lot")
        )
