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
    default_filters = defaultdict()
    filters: dict = {}
    statuses = []

    @property
    def choices(self) -> list[tuple[str, str]]:
        return [(status.name, status.label) for status in self.statuses]

    @abstractmethod
    def _get_base_queryset(self) -> QuerySet:
        pass

    def _build_queryset_filters(self) -> None:
        pass

    def _get_order_by(self) -> List:
        if not isinstance(self.order_by, list):
            self.order_by = [self.order_by]

        return [field_to_order for field_to_order in self.order_by if field_to_order]

    def get_count_for(self):
        filters = {
            **self.filters,
            "statut__in": [statut.label for statut in self.statuses],
        }
        return self._get_base_queryset().filter(**filters).count()

    def get_queryset(self) -> QuerySet:
        queryset = self._get_base_queryset()
        self._build_queryset_filters()

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
    commune: str | None
    departement: str | None
    order_by: str | None
    search_input: str | None
    commune: str | None = None
    financement: str | None = None
    statut: ConventionStatut | None = None

    def __init__(
        self,
        user: User,
        anru: bool = False,
        bailleur: Bailleur | None = None,
        administration: Administration | None = None,
        search_filters: dict | None = None,
    ):
        self.user: User = user
        self.anru: bool = anru
        self.bailleur: Bailleur | None = bailleur
        self.administration: Administration | None = administration

        if search_filters:
            for name in [
                "commune",
                "departement",
                "financement",
                "order_by",
                "search_input",
            ]:
                setattr(self, name, search_filters.get(name))
            self.statut = ConventionStatut.get_by_label(search_filters.get("statut"))

    def _build_queryset_filters(self):
        self.filters = self.default_filters

        if self.statuses:
            self.filters["statut__in"] = map(lambda s: s.label, self.statuses)

        if self.statut:
            self.filters["statut"] = self.statut.label

        if self.commune:
            self.filters["programme__ville__icontains"] = self.commune

        if self.financement:
            self.filters["financement"] = self.financement

    def _get_base_queryset(self) -> QuerySet:
        return (
            self.user.conventions()
            .prefetch_related("programme")
            .prefetch_related("programme__administration")
            .prefetch_related("lot")
        )


class UserConventionEnInstructionSearchService(UserConventionSearchService):
    weight = 0
    order_by = "programme__date_achevement_compile"
    verbose_name = "en instruction"
    statuses = [
        ConventionStatut.PROJET,
        ConventionStatut.INSTRUCTION,
        ConventionStatut.CORRECTION,
        ConventionStatut.A_SIGNER,
    ]


class UserConventionActivesSearchService(UserConventionSearchService):
    weight = 10
    order_by = "televersement_convention_signee_le"
    verbose_name = "validée(s)"
    statuses = [ConventionStatut.SIGNEE]
    default_filters = {"parent_id": None}


class UserConventionTermineesSearchService(UserConventionSearchService):
    weight = 100
    order_by = "televersement_convention_signee_le"
    verbose_name = "résiliée(s) / dénoncée(s)"
    statuses = [
        ConventionStatut.RESILIEE,
        ConventionStatut.DENONCEE,
        ConventionStatut.ANNULEE,
    ]
    default_filters = {"parent_id": None}
