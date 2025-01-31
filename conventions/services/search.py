from collections import defaultdict
from datetime import date

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Case, F, Q, QuerySet, Value, When
from django.db.models.functions import Coalesce, Round

from conventions.models import Convention, ConventionStatut
from programmes.models import Programme
from users.models import User


class ConventionSearchServiceBase:
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
        else:
            queryset = queryset.order_by("-cree_le")

        return queryset

    def paginate(self, size: int | None = None) -> Paginator:
        return Paginator(
            self.get_queryset(), size or settings.APILOS_PAGINATION_PER_PAGE
        )


class AvenantListSearchService(ConventionSearchServiceBase):
    prefetch = [
        "programme",
        # "lot",
    ]

    def __init__(self, convention: Convention, order_by: str | None = None):
        self.convention: Convention = (
            convention.parent if convention.is_avenant() else convention
        )

        if order_by:
            self.order_by = order_by

    def _get_base_queryset(self) -> QuerySet:
        return self.convention.avenants.without_denonciation_and_resiliation()


class ProgrammeConventionSearchService(ConventionSearchServiceBase):
    prefetch = [
        "programme__administration",
        # "lot",
    ]

    def __init__(self, programme: Programme, order_by: str | None = None):
        self.programme: Programme = programme

        if order_by:
            self.order_by = order_by

    def _get_base_queryset(self) -> QuerySet:
        return Convention.objects.filter(programme=self.programme)


class ConventionSearchService(ConventionSearchServiceBase):
    prefetch = [
        "programme__bailleur",
        "programme__administration",
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

    def _build_filters(self, queryset: QuerySet) -> QuerySet:  # noqa: C901
        if self.statuts:
            _statut_filters = Q(statut__in=[s.label for s in self.statuts])

            if ConventionStatut.SIGNEE in self.statuts:
                # Si on filtre sur les conventions signées,
                # on inclut égaement les conventions en cours de resiliation ou de denonciation
                if ConventionStatut.RESILIEE not in self.statuts:
                    _statut_filters |= Q(
                        statut=ConventionStatut.RESILIEE.label,
                        date_resiliation__gt=date.today(),
                    )
                if ConventionStatut.DENONCEE not in self.statuts:
                    _statut_filters |= Q(
                        statut=ConventionStatut.DENONCEE.label,
                        date_denonciation__gt=date.today(),
                    )

            queryset = queryset.filter(_statut_filters)

        if self.anru:
            queryset = queryset.filter(programme__anru=True)

        if self.avenant_seulement:
            queryset = queryset.filter(parent_id__isnull=False)

        if self.financement:
            queryset = queryset.filter(lots__financement=self.financement)

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
        return TrigramSimilarity(field_name, search_term)

    def _build_ranking(self, queryset: QuerySet) -> QuerySet:
        """
        On ajoute des annotations pour le ranking des différentes parties de la convention.
        On utilise un vector pour le nom du programme,
        et on calcule une similarité trigramme pour les numéros et le lieu.
        """

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
            _search_numero = (
                self.search_numero.replace("-", "")
                .replace("/", "")
                .replace(".", "")
                .replace(" ", "")
            )
            queryset = queryset.annotate(
                programme_numero_similarity=self._numero_trgm_similarity(
                    field_name="programme__numero_operation_pour_recherche",
                    search_term=_search_numero,
                )
            ).annotate(
                parent_conv_numero_similarity=self._numero_trgm_similarity(
                    field_name="parent__numero_pour_recherche",
                    search_term=_search_numero,
                )
            )

            if not self.avenant_seulement:
                queryset = queryset.annotate(
                    conv_numero_similarity=self._numero_trgm_similarity(
                        field_name="numero_pour_recherche", search_term=_search_numero
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
        """
        On applique les filtres de recherche sur les différentes parties de la convention.
        Pour le seuil de similarité, on utilise une valeur unique,
        définie dans les settings (TRIGRAM_SIMILARITY_THRESHOLD).
        """

        if self.search_operation_nom_query:
            queryset = queryset.filter(
                programme__search_vector=self.search_operation_nom_query
            )

        if self.search_numero:
            # Si on a moins de 5 caractères, on va effectuer une recherche de type "endswith",
            # uniquement sur les numéros de convention et non les avenants,
            # afin de conserver la recherche par numéro de convention de type "ecoloweb"
            _search_numero_n = (
                self.search_numero.replace("-", "")
                .replace("/", "")
                .replace(".", "")
                .replace(" ", "")
            )
            _search_numero_s = len(_search_numero_n)
            if _search_numero_s > 0 and _search_numero_s < 5:
                if self.avenant_seulement:
                    queryset = queryset.filter(
                        parent__numero_pour_recherche__endswith=_search_numero_n
                    )
                else:
                    queryset = queryset.filter(
                        Q(parent__isnull=True)
                        & Q(numero_pour_recherche__endswith=_search_numero_n)
                    )
            else:
                if self.avenant_seulement:
                    queryset = queryset.filter(
                        Q(
                            programme__numero_operation_pour_recherche__icontains=_search_numero_n
                        )
                        | Q(parent__numero_pour_recherche__icontains=_search_numero_n)
                    )
                else:
                    queryset = queryset.filter(
                        Q(
                            programme__numero_operation_pour_recherche__icontains=_search_numero_n
                        )
                        | Q(numero_pour_recherche__icontains=_search_numero_n)
                        | Q(parent__numero_pour_recherche__icontains=_search_numero_n)
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
        """
        On normalise les scores pour les différentes parties de la recherche,
        puis on les additionne pour obtenir un score global.
        """

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
