import re
from collections import defaultdict
from copy import copy

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Case, F, Q, QuerySet, Value, When
from django.db.models.functions import Coalesce, Replace, Round

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
        return Convention.objects.none()

    def _build_filters(self, queryset: QuerySet) -> QuerySet:
        return queryset

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

    def _get_base_queryset(self) -> QuerySet:
        return self.user.conventions()

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
    avenant_seulement: bool

    date_signature: str | None = None
    financement: str | None = None
    nature_logement: str | None = None
    statuts: list[ConventionStatut] | None = None

    search_input: str | None = None
    search_input_numbers: str | None = None
    search_query: SearchQuery | None = None

    def __init__(self, user: User, search_filters: dict | None = None) -> None:
        self.user = user
        self.anru = False
        self.avenant_seulement = False
        self.statuts = None

        if search_filters:
            self.anru = search_filters.get("anru") is not None
            self.avenant_seulement = search_filters.get("avenant_seulement") is not None
            if search_filters.get("statuts"):
                self.statuts = [
                    ConventionStatut.get_by_label(s)
                    for s in search_filters.get("statuts").split(",")
                ]
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
        if self.statuts:
            queryset = queryset.filter(statut__in=[s.label for s in self.statuts])

        if self.anru:
            queryset = queryset.filter(programme__anru=True)

        if self.avenant_seulement:
            queryset = queryset.filter(parent_id__isnull=False)

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
                # queryset.annotate(
                #     programme_nom_similarity=TrigramSimilarity(
                #         "programme__nom", self.search_input
                #     )
                # )
                .annotate(
                    # TODO: utiliser un champ composé full_adress ?
                    programme_ville_similarity=TrigramSimilarity(
                        "programme__ville", self.search_input
                    )
                )
                .annotate(
                    _r1=Replace("programme__numero_galion", Value("/")),
                    _r2=Replace("_r1", Value("-")),
                    programme_numero_similarity=TrigramSimilarity(
                        "_r2", self.search_input.replace("-", "").replace("/", "")
                    ),
                )
                # .annotate(
                #     search_vector_bailleur_rank=SearchRank(
                #         vector="programme__bailleur__search_vector",
                #         query=self.search_query,
                #     )
                # )
                .annotate(
                    bailleur_nom_similarity=TrigramSimilarity(
                        "programme__bailleur__nom", self.search_input
                    )
                )
                .annotate(
                    bailleur_siret_similarity=TrigramSimilarity(
                        Replace("programme__bailleur__siret", Value(" ")),
                        self.search_input_numbers,
                    ),
                )
                .annotate(
                    _r1=Replace("numero", Value("/")),
                    _r2=Replace("_r1", Value("-")),
                    conv_numero_similarity=TrigramSimilarity(
                        "_r2", self.search_input.replace("-", "").replace("/", "")
                    ),
                )
            )

        return queryset

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        if self.search_input:
            queryset = queryset.filter(
                Q(programme__search_vector=self.search_query)
                # Q(programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                | Q(
                    programme_ville_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                )
                | Q(
                    programme_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                )
                # | Q(programme__bailleur__search_vector=self.search_query)
                | Q(bailleur_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                | Q(bailleur_siret_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                | Q(conv_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
            )

        return queryset

    def _build_scoring(self, queryset: QuerySet) -> QuerySet:
        # TODO: construire un score global en s'appuyant sur les annotations de ranking

        if self.search_input:
            queryset = (
                queryset.annotate(
                    programme_nom_score=Round(
                        Coalesce(F("search_vector_programme_rank"), 0.0),
                        precision=2,
                    )
                )
                # queryset.annotate(
                #     programme_nom_score=Case(
                #         When(
                #             programme_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                #             then=Round(
                #                 Coalesce(F("programme_nom_similarity"), 0.0),
                #                 precision=2,
                #             ),
                #         ),
                #         default=Value(0.0),
                #     )
                # )
                .annotate(
                    programme_ville_score=Case(
                        When(
                            programme_ville_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                            then=Round(
                                Coalesce(F("programme_ville_similarity"), 0.0),
                                precision=2,
                            ),
                        ),
                        default=Value(0.0),
                    )
                )
                .annotate(
                    programme_numero_score=Case(
                        When(
                            programme_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                            then=Round(
                                Coalesce(F("programme_numero_similarity"), 0.0),
                                precision=2,
                            ),
                        ),
                        default=Value(0.0),
                    )
                )
                .annotate(
                    bailleur_nom_score=Case(
                        When(
                            bailleur_nom_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                            then=Round(
                                Coalesce(F("bailleur_nom_similarity"), 0.0),
                                precision=2,
                            ),
                        ),
                        default=Value(0.0),
                    )
                )
                .annotate(
                    bailleur_siret_score=Case(
                        When(
                            bailleur_siret_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                            then=Round(
                                Coalesce(F("bailleur_siret_similarity"), 0.0),
                                precision=2,
                            ),
                        ),
                        default=Value(0.0),
                    )
                )
                .annotate(
                    conv_numero_score=Case(
                        When(
                            conv_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                            then=Round(
                                Coalesce(F("conv_numero_similarity"), 0.0),
                                precision=2,
                            ),
                        ),
                        default=Value(0.0),
                    )
                )
                .annotate(
                    score=F("programme_nom_score")
                    + F("programme_ville_score")
                    + F("programme_numero_score")
                    + F("bailleur_nom_score")
                    + F("bailleur_siret_score")
                    + F("conv_numero_score")
                )
            )

        return queryset

    def _get_order_by(self) -> list[str]:
        order_by = super()._get_order_by()
        if self.search_input:
            order_by.append("-score")
        order_by.append("-cree_le")
        return order_by
