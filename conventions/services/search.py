from abc import ABC, abstractmethod
from typing import List, Sequence

from django.conf import settings
from django.db.models import QuerySet
from django.core.paginator import Paginator

from conventions.models import Convention, ConventionStatut
from programmes.models import Programme
from users.models import User


class ConventionSearchBaseService(ABC):
    @abstractmethod
    def get_base_query_set(self) -> QuerySet:
        pass

    def get_order_by_fields(self) -> List:
        return ["cree_le"]

    def get_query_set(self) -> QuerySet:
        return self.get_base_query_set().order_by(*self.get_order_by_fields())

    def get_total(self) -> int:
        """
        Return the total number of lines targeted by the base query, without filters
        """
        return self.get_query_set().count()

    def get_results(
        self, page: int = 1, size: int | None = None
    ) -> Sequence[Convention]:
        """
        Return the paginated list of matched conventions
        """
        return Paginator(
            self.get_query_set(), size or settings.APILOS_PAGINATION_PER_PAGE
        ).get_page(page)


class AvenantListSearchService(ConventionSearchBaseService):
    def __init__(self, convention: Convention, order_by_numero: bool = False):
        self.convention: convention = (
            convention.parent if convention.is_avenant() else convention
        )
        self.order_by_numero: bool = order_by_numero

    def get_order_by_fields(self) -> List:
        return ["numero"] if self.order_by_numero else super().get_order_by_fields()

    def get_base_query_set(self) -> QuerySet:
        return (
            self.convention.avenants.all()
            .prefetch_related("programme")
            .prefetch_related("lot")
        )


class ProgrammeConventionSearchService(ConventionSearchBaseService):
    def __init__(self, programme: Programme, order_by: str | None = None):
        self.programme: programme
        self.order_by: str | None = order_by

    def get_base_query_set(self) -> QuerySet:
        return (
            Convention.objects.filter(programme=self.programme)
            .prefetch_related("programme")
            .prefetch_related("programme__administration")
            .prefetch_related("lot")
        )

    def get_order_by_fields(self) -> List:
        return [self.order_by] if self.order_by is not None else []


class UserConventionSearchService(ConventionSearchBaseService):

    # TODO: process these filters
    #     search_input=request.GET.get("search_input", ""),
    #     order_by=request.GET.get(
    #         "order_by",
    #         "programme__date_achevement_compile"
    #         if active
    #         else "televersement_convention_signee_le",
    #     ),
    #     active=active,
    #     page=request.GET.get("page", 1),
    #     statut_filter=request.GET.get("cstatut", ""),
    #     financement_filter=request.GET.get("financement", ""),
    #     departement_input=request.GET.get("departement_input", ""),
    #     ville=request.GET.get("ville"),
    #     anru=(request.GET.get("anru") is not None),  # As anru is a checkbox
    #     user=request.user,
    #     bailleur=bailleur,
    #     administration=administration,

    def __init__(
        self, user: User, statuses: List[ConventionStatut], order_by: str | None = None
    ):
        self.user: User = user
        self.order_by: str | None = order_by
        self.statuses = statuses

    def get_base_query_set(self) -> QuerySet:
        return (
            self.user.conventions()
            .prefetch_related("programme")
            .prefetch_related("programme__administration")
            .prefetch_related("lot")
            .filter(statut__in=map(lambda s: s.label, self.statuses))
        )
