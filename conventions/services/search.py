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
    bailleur: str | None = None

    search_operation_nom: str | None = None
    search_operation_nom_query: SearchQuery | None = None
    search_numero: str | None = None
    search_lieu: str | None = None

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
                "bailleur",
                "date_signature",
                "financement",
                "nature_logement",
                "search_lieu",
                "search_numero",
                "search_operation_nom",
            ):
                setattr(self, name, search_filters.get(name))

            if self.search_operation_nom:
                self.search_operation_nom_query = SearchQuery(
                    self.search_operation_nom, config="french"
                )

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

        if self.bailleur:
            queryset = queryset.filter(programme__bailleur__uuid=self.bailleur)

        return queryset

    def _numero_trgm_similarity(
        self, field_name: str, search_term: str
    ) -> TrigramSimilarity:
        return TrigramSimilarity(
            Replace(Replace(field_name, Value("/")), Value("-")), search_term
        )

    def _build_ranking(self, queryset: QuerySet) -> QuerySet:
        queryset = queryset.annotate(
            _is_avenant=Case(
                When(parent__isnull=False, then=Value(True)), default=False
            )
        )

        if self.search_operation_nom_query:
            queryset = queryset.annotate(
                search_vector_programme_nom_rank=SearchRank(
                    vector="programme__search_vector",
                    query=self.search_operation_nom_query,
                )
            )

        if self.search_numero:
            _search_numero = self.search_numero.replace("-", "").replace("/", "")
            queryset = queryset.annotate(
                programme_numero_similarity=self._numero_trgm_similarity(
                    field_name="programme__numero_galion",
                    search_term=_search_numero,
                )
            ).annotate(
                parent_conv_numero_similarity=self._numero_trgm_similarity(
                    field_name="parent__numero", search_term=_search_numero
                )
            )

            if not self.avenant_seulement:
                queryset = queryset.annotate(
                    conv_numero_similarity=self._numero_trgm_similarity(
                        field_name="numero", search_term=_search_numero
                    )
                )

        if self.search_lieu:
            queryset = queryset.annotate(
                programme_ville_similarity=TrigramSimilarity(
                    "programme__ville", self.search_lieu
                )
            ).annotate(
                programme_code_postal_similarity=TrigramSimilarity(
                    "programme__code_postal", self.search_lieu
                )
            )

        return queryset

    def _build_search_filters(self, queryset: QuerySet) -> QuerySet:
        if self.search_operation_nom_query:
            queryset = queryset.filter(
                programme__search_vector=self.search_operation_nom_query
            )

        if self.search_numero:
            if len(self.search_numero) == 4:
                if self.avenant_seulement:
                    queryset = queryset.filter(
                        parent__numero__endswith=self.search_numero
                    )
                else:
                    queryset = queryset.filter(
                        Q(numero__endswith=self.search_numero)
                        | Q(parent__numero__endswith=self.search_numero)
                    )
            else:
                if self.avenant_seulement:
                    queryset = queryset.filter(
                        Q(
                            programme_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                        )
                        | Q(
                            parent_conv_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                        )
                    )
                else:
                    queryset = queryset.filter(
                        Q(
                            programme_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                        )
                        | Q(
                            conv_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                        )
                        | Q(
                            parent_conv_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                        )
                    )

        if self.search_lieu:
            queryset = queryset.filter(
                Q(programme_ville_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                | Q(
                    programme_code_postal_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD
                )
            )

        return queryset

    def _build_scoring(self, queryset: QuerySet) -> QuerySet:
        if self.search_operation_nom:
            queryset = queryset.annotate(
                programme_nom_score=(
                    Round(
                        Coalesce(F("search_vector_programme_nom_rank"), 0.0),
                        precision=2,
                    )
                )
            )
        else:
            queryset = queryset.annotate(programme_nom_score=Value(0.0))

        if self.search_numero:
            queryset = queryset.annotate(
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
            ).annotate(
                parent_conv_numero_score=Case(
                    When(
                        parent_conv_numero_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                        then=Round(
                            Coalesce(F("parent_conv_numero_similarity"), 0.0),
                            precision=2,
                        ),
                    ),
                    default=Value(0.0),
                )
            )

            if not self.avenant_seulement:
                queryset = queryset.annotate(
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
            else:
                queryset = queryset.annotate(conv_numero_score=Value(0.0))
        else:
            queryset = queryset.annotate(
                programme_numero_score=Value(0.0),
                conv_numero_score=Value(0.0),
                parent_conv_numero_score=Value(0.0),
            )

        if self.search_lieu:
            queryset = queryset.annotate(
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
            ).annotate(
                programme_code_postal_score=Case(
                    When(
                        programme_code_postal_similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD,
                        then=Round(
                            Coalesce(F("programme_code_postal_similarity"), 0.0),
                            precision=2,
                        ),
                    ),
                    default=Value(0.0),
                )
            )
        else:
            queryset = queryset.annotate(
                programme_ville_score=Value(0.0),
                programme_code_postal_score=Value(0.0),
            )

        if self.avenant_seulement:
            return queryset.annotate(
                score=(
                    F("programme_nom_score")
                    + F("programme_numero_score")
                    + F("parent_conv_numero_score")
                    + F("programme_ville_score")
                    + F("programme_code_postal_score")
                )
            )

        return queryset.annotate(
            score=(
                F("programme_nom_score")
                + F("programme_numero_score")
                + F("conv_numero_score")
                + F("parent_conv_numero_score")
                + F("programme_ville_score")
                + F("programme_code_postal_score")
                + Case(
                    When(_is_avenant=True, then=Value(-0.3)),
                    default=Value(0.0),
                )
            )
        )

    def _get_order_by(self) -> list[str]:
        return super()._get_order_by() + ["-score", "-cree_le"]
