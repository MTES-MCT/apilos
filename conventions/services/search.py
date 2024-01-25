from abc import ABC, abstractmethod
from collections import defaultdict
from copy import copy

from django.conf import settings
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet, Value
from django.db.models.functions import Replace

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
    extra_filters = None
    statuses = []

    @property
    def choices(self) -> list[tuple[str, str]]:
        return [(status.name, status.label) for status in self.statuses]

    @abstractmethod
    def _get_base_queryset(self) -> QuerySet:
        pass

    def _build_queryset_filters(self) -> None:
        pass

    def _build_queryset_extra_filters(self) -> None:
        pass

    def _get_order_by(self) -> list:
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
        self._build_queryset_extra_filters()

        if self.filters:
            queryset = queryset.filter(**self.filters)

        if self.extra_filters:
            queryset = queryset.filter(self.extra_filters)

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
        return self.convention.avenants.without_denonciation_and_resiliation()


class ProgrammeConventionSearchService(ConventionSearchBaseService):
    prefetch = ["programme", "programme__administration", "lot"]

    def __init__(self, programme: Programme, order_by: str | None = None):
        self.programme: Programme = programme

        if order_by:
            self.order_by = order_by

    def _get_base_queryset(self) -> QuerySet:
        return Convention.objects.filter(programme=self.programme)


class UserConventionSearchService(ConventionSearchBaseService):
    prefetch = ["programme__administration", "lot"]

    commune: str | None
    departement: str | None
    order_by: str | None
    search_input: str | None = None
    commune: str | None = None
    financement: str | None = None
    statut: ConventionStatut | None = None
    bailleur: Bailleur | None = None
    administration: Administration | None = None
    date_validation: str | None = None

    def __init__(
        self,
        user: User,
        anru: bool = False,
        search_filters: dict | None = None,
    ):
        self.user: User = user
        self.anru: bool = anru

        if search_filters:
            for name in [
                "commune",
                "departement",
                "financement",
                "order_by",
                "search_input",
                "bailleur",
                "administration",
                "date_validation",
            ]:
                setattr(self, name, search_filters.get(name))
            self.statut = ConventionStatut.get_by_label(search_filters.get("statut"))

    def _build_queryset_filters(self):
        self.filters = copy(self.default_filters)

        if self.statuses:
            self.filters["statut__in"] = map(lambda s: s.label, self.statuses)

        if self.statut:
            self.filters["statut"] = self.statut.label

        if self.commune:
            self.filters["vector_ville"] = self.commune

        if self.financement:
            self.filters["financement"] = self.financement

        if self.bailleur:
            self.filters["lot__programme__bailleur__uuid"] = self.bailleur

        if self.administration:
            self.filters["lot__programme__administration__uuid"] = self.administration

        if self.anru:
            self.filters["lot__programme__anru"] = True

        if self.date_validation:
            self.filters["valide_le__year"] = self.date_validation

    def _get_base_queryset(self) -> QuerySet:
        qs = self.user.conventions()

        if self.search_input:
            qs = qs.annotate(
                programme_nom_similarity=TrigramSimilarity(
                    "programme__nom", self.search_input
                )
            )

        if self.commune:
            qs = qs.annotate(
                vector_ville=(SearchVector("programme__ville", config="french"))
            )

        return qs

    def _get_order_by(self) -> list:
        order_by = super()._get_order_by()

        if self.search_input:
            order_by.append("-programme_nom_similarity")

        return order_by


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

    def _build_queryset_extra_filters(self):
        super()._build_queryset_extra_filters()
        if self.search_input:
            self.extra_filters = (
                Q(programme__nom__icontains=self.search_input)
                | Q(programme__code_postal__icontains=self.search_input)
                | Q(programme__numero_galion__icontains=self.search_input)
                | Q(programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            )


class UserConventionActivesSearchService(UserConventionSearchService):
    weight = 10
    order_by = "televersement_convention_signee_le"
    verbose_name = "validée(s)"
    statuses = [ConventionStatut.SIGNEE]
    default_filters = {"parent_id": None}

    def _get_base_queryset(self) -> QuerySet:
        qs = super()._get_base_queryset()

        if self.search_input:
            qs = qs.annotate(
                _r1=Replace("numero", Value("/")),
                _r2=Replace("_r1", Value("-")),
                _r3=Replace("_r2", Value(" ")),
                numero_similarity=TrigramSimilarity(
                    "_r3",
                    self.search_input.replace("-", "")
                    .replace("/", "")
                    .replace(" ", ""),
                ),
            )

        return qs

    def _build_queryset_extra_filters(self):
        super()._build_queryset_extra_filters()
        if self.search_input:
            self.extra_filters = (
                Q(programme__nom__icontains=self.search_input)
                | Q(programme__code_postal__icontains=self.search_input)
                | Q(programme__numero_galion__icontains=self.search_input)
                | Q(numero__icontains=self.search_input)
                | Q(numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                | Q(programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            )

    def _get_order_by(self) -> list:
        qs = super()._get_order_by()

        if self.search_input:
            qs.append("-numero_similarity")

        return qs


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

    def _build_queryset_extra_filters(self):
        super()._build_queryset_extra_filters()
        if self.search_input:
            self.extra_filters = (
                Q(programme__nom__icontains=self.search_input)
                | Q(programme__code_postal__icontains=self.search_input)
                | Q(programme__numero_galion__icontains=self.search_input)
                | Q(numero__icontains=self.search_input)
                | Q(programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            )
