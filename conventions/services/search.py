import re
from collections import defaultdict
from copy import copy

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Count, Q, QuerySet, Value
from django.db.models.functions import Replace

from bailleurs.models import Bailleur
from conventions.models import Convention, ConventionStatut
from instructeurs.models import Administration
from programmes.models import Programme
from users.models import User


class ConventionSearchBaseService:
    order_by = None
    prefetch = []
    default_filters = defaultdict()

    def _get_base_queryset(self) -> QuerySet:
        pass

    def _build_filters(self, queryset: QuerySet) -> QuerySet:
        pass

    def _build_ranking(self, queryset: QuerySet) -> QuerySet:
        return queryset

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        return queryset

    def _build_scoring(self, queryset: QuerySet) -> QuerySet:
        return queryset

    def _get_order_by(self) -> list[str]:
        if not isinstance(self.order_by, list):
            self.order_by = [self.order_by]

        return [field_to_order for field_to_order in self.order_by if field_to_order]

    def get_queryset(self) -> QuerySet:
        queryset = self._get_base_queryset()
        queryset = self._build_filters(queryset)
        queryset = self._build_ranking(queryset)
        queryset = self._build_search_filters(queryset)
        queryset = self._build_scoring(queryset)

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
    prefetch = [
        "programme__administration",
        "lot",
    ]

    def __init__(self, programme: Programme, order_by: str | None = None):
        self.programme: Programme = programme

        if order_by:
            self.order_by = order_by

    def _get_base_queryset(self) -> QuerySet:
        return Convention.objects.filter(programme=self.programme)


class UserConventionSearchService(ConventionSearchBaseService):
    prefetch = [
        "programme__bailleur",
        "programme__administration",
        "lot",
    ]

    user: User
    anru: bool

    commune: str | None
    departement: str | None
    order_by: str | None
    search_input: str | None = None
    commune: str | None = None
    financement: str | None = None
    statut: ConventionStatut | None = None
    bailleur: Bailleur | None = None
    administration: Administration | None = None
    date_signature: str | None = None

    statuses = []

    def __init__(self, user: User, search_filters: dict | None = None):
        self.user = user
        self.anru = False

        if search_filters:
            for name in [
                "commune",
                "departement",
                "financement",
                "order_by",
                "search_input",
                "bailleur",
                "administration",
                "date_signature",
            ]:
                setattr(self, name, search_filters.get(name))
            self.statut = ConventionStatut.get_by_label(search_filters.get("statut"))
            self.anru = search_filters.get("anru") is not None

    @property
    def choices(self) -> list[tuple[str, str]]:
        return [(status.name, status.label) for status in self.statuses]

    def _build_filters(self, queryset: QuerySet) -> QuerySet:
        filters = copy(self.default_filters)

        if self.statuses:
            filters["statut__in"] = map(lambda s: s.label, self.statuses)

        if self.statut:
            filters["statut"] = self.statut.label

        if self.financement:
            filters["financement"] = self.financement

        if self.bailleur:
            filters["lot__programme__bailleur__uuid"] = self.bailleur

        if self.administration:
            filters["lot__programme__administration__uuid"] = self.administration

        if self.anru:
            filters["lot__programme__anru"] = True

        if self.date_signature:
            filters["televersement_convention_signee_le__year"] = self.date_signature

        return queryset.filter(**filters)

    def _build_ranking(self, queryset: QuerySet) -> QuerySet:
        if self.search_input:
            queryset = queryset.annotate(
                programme_nom_similarity=TrigramSimilarity(
                    "programme__nom", self.search_input
                )
            )

        if self.commune:
            queryset = queryset.annotate(
                programme_ville_similarity=TrigramSimilarity(
                    "programme__ville", self.commune
                )
            )

        return queryset

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        if self.commune:
            queryset = queryset.filter(
                programme_ville_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
            )

        return queryset

    def _get_order_by(self) -> list:
        order_by = super()._get_order_by()

        if self.commune:
            order_by.append("-programme_ville_similarity")

        if self.search_input:
            order_by.append("-programme_nom_similarity")

        order_by.append("-cree_le")
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

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        queryset = super()._build_search_filters(queryset)

        if self.search_input:
            queryset = queryset.filter(
                Q(programme__nom__icontains=self.search_input)
                | Q(programme__code_postal__icontains=self.search_input)
                | Q(programme__numero_galion__icontains=self.search_input)
                | Q(programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            )

        return queryset


class UserConventionActivesSearchService(UserConventionSearchService):
    weight = 10
    order_by = "televersement_convention_signee_le"
    verbose_name = "validée(s)"
    statuses = [ConventionStatut.SIGNEE]
    default_filters = {"parent_id": None}

    def _build_ranking(self, queryset: QuerySet) -> QuerySet:
        queryset = super()._build_ranking(queryset)

        if self.search_input:
            queryset = queryset.annotate(
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

        return queryset

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        queryset = super()._build_search_filters(queryset)

        if self.search_input:
            queryset = queryset.filter(
                Q(programme__nom__icontains=self.search_input)
                | Q(programme__code_postal__icontains=self.search_input)
                | Q(programme__numero_galion__icontains=self.search_input)
                | Q(numero__icontains=self.search_input)
                | Q(numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                | Q(programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            )

        return queryset

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

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        queryset = super()._build_search_filters(queryset)

        if self.search_input:
            queryset = queryset.filter(
                Q(programme__nom__icontains=self.search_input)
                | Q(programme__code_postal__icontains=self.search_input)
                | Q(programme__numero_galion__icontains=self.search_input)
                | Q(numero__icontains=self.search_input)
                | Q(programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            )
        return queryset


class UserConventionSmartSearchService(ConventionSearchBaseService):
    prefetch = [
        "programme__bailleur",
        "programme__administration",
        "lot",
    ]

    user: User
    anru: bool
    avec_avenant: bool

    date_signature: str | None = None
    financement: str | None = None
    nature_logement: str | None = None
    statut: ConventionStatut | None = None

    search_input: str | None = None
    search_input_numbers: str | None = None
    search_query: SearchQuery | None = None

    def __init__(self, user: User, search_filters: dict | None = None) -> None:
        self.user = user
        self.anru = False
        self.avec_avenant = False

        if search_filters:
            self.anru = search_filters.get("anru") is not None
            self.avec_avenant = search_filters.get("avec_avenant") is not None
            self.statut = ConventionStatut.get_by_label(search_filters.get("statut"))
            for name in (
                "date_signature",
                "financement",
                "nature_logement",
                "search_input",
            ):
                setattr(self, name, search_filters.get(name))

            if self.search_input:
                self.search_query = SearchQuery(self.search_input, config="french")
                self.search_input_numbers = " ".join(
                    re.findall(r"\d+", self.search_input)
                ).strip()

    def _get_base_queryset(self) -> QuerySet:
        return self.user.conventions()

    def _build_filters(self, queryset: QuerySet) -> QuerySet:
        if self.statut:
            queryset = queryset.filter(statut=self.statut.label)

        if self.anru:
            queryset = queryset.filter(programme__anru=True)

        if self.avec_avenant:
            queryset = queryset.annotate(count_avenants=Count("avenants")).filter(
                count_avenants__gt=0
            )

        if self.financement:
            queryset = queryset.filter(financement=self.financement)

        if self.nature_logement:
            queryset = queryset.filter(programme__nature_logement=self.nature_logement)

        if self.date_signature:
            queryset = queryset.filter(
                televersement_convention_signee_le__year=self.date_signature
            )

        return queryset

    def _build_ranking(self, queryset: QuerySet) -> QuerySet:
        if self.search_input:
            queryset = (
                queryset.annotate(
                    search_vector_programme_rank=SearchRank(
                        vector="programme__search_vector",
                        query=self.search_query,
                    )
                )
                .annotate(
                    search_vector_bailleur_rank=SearchRank(
                        vector="programme__bailleur__search_vector",
                        query=self.search_query,
                    )
                )
                .annotate(
                    programme_ville_similarity=TrigramSimilarity(
                        "programme__ville", self.search_input
                    )
                )
                .annotate(
                    _r1=Replace("numero", Value("/")),
                    _r2=Replace("_r1", Value("-")),
                    numero_similarity=TrigramSimilarity(
                        "_r2", self.search_input.replace("-", "").replace("/", "")
                    ),
                )
                .annotate(
                    _r1=Replace("programme__numero_galion", Value("/")),
                    _r2=Replace("_r1", Value("-")),
                    numero_operation_similarity=TrigramSimilarity(
                        "_r2", self.search_input.replace("-", "").replace("/", "")
                    ),
                )
            )

        if len(self.search_input_numbers):
            queryset = queryset.annotate(
                bailleur_siret_similarity=TrigramSimilarity(
                    Replace("programme__bailleur__siret", Value(" ")),
                    self.search_input_numbers,
                ),
            )

        return queryset

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        if self.search_input:
            extra_filters = (
                Q(programme__search_vector=self.search_query)
                | Q(programme__bailleur__search_vector=self.search_query)
                | Q(numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                | Q(
                    numero_operation_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                )
                | Q(
                    programme_ville_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                )
            )

            if len(self.search_input_numbers):
                extra_filters |= Q(
                    bailleur_siret_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                )

            queryset = queryset.filter(extra_filters)

    def _build_scoring(self, queryset: QuerySet) -> QuerySet:
        queryset = super()._build_scoring(queryset)
        # TODO: construire un score global en s'appuyant sur les annotations de ranking
        return queryset

    def _get_order_by(self) -> list[str]:
        order_by = super()._get_order_by()

        # TODO: trier par score global
        if self.search_input:
            order_by += [
                "-numero_similarity",
                "-numero_operation_similarity",
                "-programme_ville_similarity",
                "-search_vector_programme_rank",
                "-search_vector_bailleur_rank",
            ]

        if len(self.search_input_numbers):
            order_by += [
                "-bailleur_siret_similarity",
            ]

        order_by.append("-cree_le")
        return order_by
